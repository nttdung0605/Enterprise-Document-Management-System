import socket

import auth
import document

import hashlib

import audit

class TCPServer:

    def __init__(
        self,
        host="127.0.0.1",
        port=5000
    ):

        self.host = host
        self.port = port

        self.auth_service = (
            auth.AuthService()
        )

        self.document_service = (
            document.DocumentService()
        )

        self.audit_service = (
            audit.AuditService()
        )

    def start(self):

        server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        server_socket.bind(
            (
                self.host,
                self.port
            )
        )

        server_socket.listen(5)

        print(
            f"[SERVER] Listening on "
            f"{self.host}:{self.port}"
        )

        while True:

            client_socket, addr = (
                server_socket.accept()
            )

            print(
                f"[CONNECTED] {addr}"
            )

            self.handle_client(
                client_socket,
                addr
            )

    def handle_client(
        self,
        client_socket,
        address
    ):

        try:
            self.current_client = (
                client_socket
            )

            while True:

                self.client_ip = (
                    address[0]
                )

                data = (
                    client_socket.recv(
                        1024
                    )
                )

                if not data:
                    break

                message = (
                    data.decode().strip()
                )

                print(
                    "[CLIENT]",
                    message
                )

                response = (
                    self.process_command(
                        message
                    )
                )

                client_socket.send(
                    response.encode()
                )

        except Exception as e:

            print(
                "[ERROR]",
                e
            )

        finally:

            client_socket.close()

    def process_command(
        self,
        message
    ):

        parts = (
            message.split()
        )

        if len(parts) == 0:
            return "INVALID_COMMAND"

        command = (
            parts[0].upper()
        )

        if command == "LOGIN":

            if len(parts) != 3:
                return (
                    "USAGE: "
                    "LOGIN username password"
                )

            username = parts[1]
            password = parts[2]

            success, token = (
                self.auth_service.login(
                    username,
                    password
                )
            )

            if success:
                return (
                    f"LOGIN_SUCCESS|{token}"
                )

            return "LOGIN_FAILED"

        elif command == "LOGOUT":

            if len(parts) != 2:
                return (
                    "USAGE: LOGOUT token"
                )

            token = parts[1]

            success = (
                self.auth_service.logout(
                    token
                )
            )

            if success:
                return (
                    "LOGOUT_SUCCESS"
                )

            return (
                "INVALID_TOKEN"
            )

        elif command == "HELP":

            return (
                "LOGIN\n"
                "LOGOUT\n"
                "UPLOAD\n"
                "LIST_PENDING\n"
                "LIST_AVAILABLE\n"
                "APPROVE\n"
                "DOWNLOAD"
            )
    
        elif command == "UPLOAD":       

            if len(parts) != 4:
                return (
                    "USAGE: "
                    "UPLOAD token "
                    "filename filesize"
                )       

            token = parts[1]
            filename = parts[2]
            filesize = int(
                parts[3]
            )       

            session = (
                self.require_auth(
                    token
                )
            )       

            if not session:
                return (
                    "INVALID_TOKEN"
                )       

            return (
                self.handle_upload(
                    filename,
                    filesize,
                    session
                )
            ) 

        elif command == "LIST_PENDING":
                
            if len(parts) != 2:
                return (
                    "USAGE: "
                    "LIST_PENDING token"
                )
        
            token = parts[1]
        
            session = (
                self.require_auth(
                    token
                )
            )
        
            if not session:
                return (
                    "INVALID_TOKEN"
                )
        
            if (
                session["role"]
                != "manager"
                and
                session["role"]
                != "admin"
            ):
                return (
                    "PERMISSION_DENIED"
                )
        
            rows = (
                self.document_service
                .list_pending(
                    session[
                        "department_id"
                    ]
                )
            )
        
            if len(rows) == 0:
                return (
                    "NO_PENDING_DOCUMENT"
                )
        
            response = []
        
            for row in rows:
            
                response.append(
                    f"{row['id']}|"
                    f"{row['filename']}|"
                    f"{row['username']}|"
                    f"{row['status']}"
                )
        
            return "\n".join(
                response
            )

        elif command == "LIST_AVAILABLE":

            if len(parts) != 2:
                return (
                    "USAGE: "
                    "LIST_AVAILABLE token"
                )

            token = parts[1]

            session = (
                self.require_auth(
                    token
                )
            )

            if not session:
                return (
                    "INVALID_TOKEN"
                )

            rows = (
                self.document_service
                .list_available(
                    session[
                        "department_id"
                    ]
                )
            )

            if len(rows) == 0:
                return (
                    "NO_AVAILABLE_DOCUMENT"
                )

            response = []

            for row in rows:
            
                response.append(
                    f"{row['id']}|"
                    f"{row['filename']}|"
                    f"{row['username']}|"
                    f"{row['status']}"
                )

            return "\n".join(
                response
            )

        elif command == "APPROVE":

            if len(parts) != 3:
                return (
                    "USAGE: "
                    "APPROVE token version_id"
                )

            token = parts[1]
            version_id = parts[2]

            session = (
                self.require_auth(
                    token
                )
            )

            if not session:
                return (
                    "INVALID_TOKEN"
                )

            if (
                session["role"]
                not in [
                    "manager",
                    "admin"
                ]
            ):
                return (
                    "PERMISSION_DENIED"
                )

            success, error = (
                self.document_service
                .update_status(
                    version_id,
                    "approved",
                    session
                )
            )

            if success:
                self.audit_service.log_action(
                    "APPROVE",
                    session["user_id"],
                    int(version_id),
                    self.client_ip
                )

                return (
                    "APPROVE_SUCCESS"
                )

            return error

        elif command == "REJECT":

            if len(parts) != 3:
                return (
                    "USAGE: "
                    "REJECT token version_id"
                )

            token = parts[1]
            version_id = parts[2]

            session = (
                self.require_auth(
                    token
                )
            )

            if not session:
                return (
                    "INVALID_TOKEN"
                )

            if (
                session["role"]
                not in [
                    "manager",
                    "admin"
                ]
            ):
                return (
                    "PERMISSION_DENIED"
                )

            success, error = (
                self.document_service
                .update_status(
                    version_id,
                    "rejected",
                    session
                )
            )

            if success:
                self.audit_service.log_action(
                    "REJECT",
                    session["user_id"],
                    int(version_id),
                    self.client_ip
                )

                return (
                    "REJECT_SUCCESS"
                )

            return error

        elif command == "DOWNLOAD":

            if len(parts) != 3:
                return (
                    "USAGE: "
                    "DOWNLOAD token version_id"
                )

            token = parts[1]
            version_id = parts[2]

            session = (
                self.require_auth(
                    token
                )
            )

            if not session:
                return (
                    "INVALID_TOKEN"
                )

            return (
                self.handle_download(
                    version_id,
                    session
                )
            )

        elif command == "LIST_AUDIT":

            if len(parts) != 2:
                return (
                    "USAGE: "
                    "LIST_AUDIT token"
                )

            token = parts[1]

            session = (
                self.require_auth(
                    token
                )
            )

            if not session:
                return (
                    "INVALID_TOKEN"
                )

            if (
                session["role"]
                != "admin"
            ):
                return (
                    "PERMISSION_DENIED"
                )

            rows = (
                self.audit_service
                .get_logs()
            )

            response = []

            for row in rows:
            
                response.append(
                    f"{row['id']}|"
                    f"{row['action']}|"
                    f"{row['username']}|"
                    f"version="
                    f"{row['version_id']}|"
                    f"{row['client_ip']}|"
                    f"{row['action_time']}"
                )

            return "\n".join(
                response
            )

        elif command == "LIST_VERSIONS":
                
            if len(parts) != 3:
                return (
                    "USAGE: "
                    "LIST_VERSIONS token filename"
                )
        
            token = parts[1]
            filename = parts[2]
        
            session = self.require_auth(
                token
            )
        
            if not session:
                return "INVALID_TOKEN"
        
            rows = (
                self.document_service
                .list_versions(
                    filename,
                    session[
                        "department_id"
                    ]
                )
            )
        
            if not rows:
                return (
                    "NO_VERSIONS_FOUND"
                )
        
            response = []
        
            for row in rows:
            
                response.append(
                    f"v{row['version_num']}|"
                    f"id={row['id']}|"
                    f"{row['status']}|"
                    f"{row['username']}|"
                    f"{row['upload_time']}"
                )
        
            return "\n".join(
                response
            )

        return (
            "UNKNOWN_COMMAND"
        )

    def handle_upload(
        self,
        filename,
        filesize,
        session
    ):

        self.current_client.send(
            b"READY_UPLOAD"
        )

        received = b""

        while len(received) < filesize:

            chunk = (
                self.current_client.recv(
                    4096
                )
            )

            if not chunk:
                break

            received += chunk

        success, version_id = (
            self.document_service
            .upload_binary_document(
                filename,
                received,
                session
            )
        )

        if success:
            self.audit_service.log_action(
                "UPLOAD",
                session["user_id"],
                version_id,
                self.client_ip
            )

            return (
                "UPLOAD_SUCCESS|PENDING"
            )

        return (
            "UPLOAD_FAILED"
        )

    def handle_download(
        self,
        version_id,
        session
    ):
    
        success, result = (
            self.document_service
            .get_download_file(
                version_id
            )
        )
    
        if not success:
            return result
    
        filepath = (
            result["filepath"]
        )
    
        filename = (
            result["filename"]
        )
    
        filesize = (
            result["filesize"]
        )
    
        expected_checksum = (
            result["checksum"]
        )
    
        try:
        
            with open(
                filepath,
                "rb"
            ) as file:
    
                file_bytes = (
                    file.read()
                )
    
            actual_checksum = (
                hashlib.sha256(
                    file_bytes
                ).hexdigest()
            )
    
            if (
                actual_checksum
                != expected_checksum
            ):
                return (
                    "FILE_CORRUPTED"
                )
    
            self.current_client.send(
                (
                    f"READY_DOWNLOAD "
                    f"{filename} "
                    f"{filesize}"
                ).encode()
            )
    
            self.current_client.send(
                file_bytes
            )
    
            self.audit_service.log_action(
                "DOWNLOAD",
                session["user_id"],
                int(version_id),
                self.client_ip
            )

            return (
                "DOWNLOAD_SUCCESS"
            )
    
        except Exception as e:
        
            print(
                "[DOWNLOAD ERROR]",
                e
            )
    
            return (
                "DOWNLOAD_FAILED"
            )

    def require_auth(
        self,
        token
    ):

        session = (
            self.auth_service
            .get_session(token)
        )

        if not session:
            return None

        return session
