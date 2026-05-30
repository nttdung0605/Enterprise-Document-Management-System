#include "client.h"

#include <iostream>
#include <string>

#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32.lib")

bool Client::connectToServer(
    const std::string& ip,
    int port
)
{
    WSADATA wsaData;

    int result = WSAStartup(
        MAKEWORD(2, 2),
        &wsaData
    );

    if (result != 0)
    {
        return false;
    }

    sock = socket(
        AF_INET,
        SOCK_STREAM,
        IPPROTO_TCP
    );

    if (sock == INVALID_SOCKET)
    {
        return false;
    }

    sockaddr_in serverAddr;

    serverAddr.sin_family =
        AF_INET;

    serverAddr.sin_port =
        htons(port);

    serverAddr.sin_addr.s_addr =
        inet_addr(
            ip.c_str()
        );

    result = connect(
        sock,
        (sockaddr*)&serverAddr,
        sizeof(serverAddr)
    );

    if (result == SOCKET_ERROR)
    {
        return false;
    }

    std::cout
        << "Connected!\n";

    return true;
}

void Client::startCLI()
{
    std::string command;

    char buffer[1024];

    while (true)
    {
        std::cout << "> ";

        std::getline(
            std::cin,
            command
        );

        if (
            command == "exit"
        )
        {
            break;
        }

        send(
            sock,
            command.c_str(),
            command.size(),
            0
        );

        memset(
            buffer,
            0,
            sizeof(buffer)
        );

        recv(
            sock,
            buffer,
            sizeof(buffer),
            0
        );

        std::cout
            << buffer
            << "\n";
    }

    closesocket(sock);

    WSACleanup();
}