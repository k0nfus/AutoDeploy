import os
import subprocess
import datetime
import paramiko

def log_message(message):
    log_file = "deploylog.txt"
    timestamp = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def run_local_command(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Lokaler Befehl '{' '.join(cmd)}' schlug fehl:\n{result.stderr}")
    return result

def main():
    # Lokaler Ordner des Blogs
    blog_dir = "/pfad/zum/Blog/"
    try:
        # Schritt 1: Git-Befehle lokal ausführen
        print("Führe 'git add .' aus ...")
        run_local_command(["git", "add", "."], blog_dir)

        # Erzeuge den Commit-Text mit aktuellem Datum und Uhrzeit im Format "JJ-MM-TT HH:MM"
        commit_message = datetime.datetime.now().strftime("%y-%m-%d %H:%M")
        print(f"Führe 'git commit -m \"{commit_message}\"' aus ...")
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=blog_dir,
            capture_output=True,
            text=True
        )
        # Wenn nichts zu committen ist, liefert git einen entsprechenden Hinweis.
        if commit_result.returncode != 0:
            if "nothing to commit" in commit_result.stderr.lower() or "nothing to commit" in commit_result.stdout.lower():
                print("Nichts zu committen.")
            else:
                raise Exception(f"Git commit schlug fehl:\n{commit_result.stderr}")

        print("Führe 'git push' aus ...")
        run_local_command(["git", "push"], blog_dir)

        # Schritt 2: Auf den VPS verbinden
        vps_ip = "ip"           # Ersetze "ip" durch die tatsächliche IP-Adresse
        vps_password = "passwort"  # Das Passwort für den VPS
        print(f"Stelle SSH-Verbindung zu {vps_ip} her ...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps_ip, username="benutzer", password=vps_password)

        # Schritt 3: Remote-Befehle ausführen
        remote_commands = [
            "sudo service gunicorn stop",
            "sudo service nginx stop",
            "cd /pfad/zum/Blog/ && git pull",
            "sudo service gunicorn start",
            "sudo service nginx start"
        ]

        for command in remote_commands:
            print(f"Führe remote Befehl '{command}' aus ...")
            stdin, stdout, stderr = ssh.exec_command(command)
            # Warten, bis der Befehl beendet ist und den Exit-Status ermitteln
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                error = stderr.read().decode()
                raise Exception(f"Remote Befehl '{command}' schlug fehl (Exit-Status {exit_status}):\n{error}")

        ssh.close()
        print("Deployment erfolgreich durchgeführt.")
        log_message("Deployment erfolgreich durchgeführt.")

    except Exception as e:
        log_message(f"Deployment fehlgeschlagen: {e}")
        print("Fehler beim Deployment:", e)

if __name__ == "__main__":
    main()

