import socket

from auth import AuthService
from document import DocumentService

class TCPServer:

    def __init__(
        self,
        host="127.0.0.1",
        port=5000
    ):

        self.host = host
        self.port = port

        self.auth_service = (
            AuthService()
        )

        self.document_service = (
            DocumentService()
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
                client_socket
            )

    def handle_client(
        self,
        client_socket
    ):

        try:

            while True:

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
                "LOGIN username password\n"
                "LOGOUT token"
            )
    
        elif command == "UPLOAD":
                
            if len(parts) != 3:
                return (
                    "USAGE: "
                    "UPLOAD token filename"
                )
        
            token = parts[1]
            filename = parts[2]
        
            session = (
                self.require_auth(
                    token
                )
            )
        
            if not session:
                return (
                    "INVALID_TOKEN"
                )
        
            success = (
                self.document_service
                .upload_document(
                    filename,
                    session
                )
            )
        
            if success:
                return (
                    "UPLOAD_SUCCESS|PENDING"
                )
        
            return (
                "UPLOAD_FAILED"
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

        return (
            "UNKNOWN_COMMAND"
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
