import server as server_


def main() -> None:
    server = server_.TCPServer()
    server.start()


if __name__ == "__main__":
    main()