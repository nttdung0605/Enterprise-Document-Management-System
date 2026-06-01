#include "client.h"

#include <iostream>
#include <string>

#include <winsock2.h>
#include <ws2tcpip.h>

#include <fstream>
#include <filesystem>

#include <sstream>
#include <vector>

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

        if (
            command.rfind(
                "UPLOAD_FILE",
                0
            ) == 0
        )
        {
            std::stringstream ss(
                command
            );
        
            std::string cmd;
            std::string token;
            std::string path;
        
            ss
            >> cmd
            >> token;
        
            std::getline(
                ss,
                path
            );
        
            if (
                !path.empty()
                &&
                path[0] == ' '
            )
            {
                path.erase(
                    0,
                    1
                );
            }
        
            uploadFile(
                token,
                path
            );
        
            continue;
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

void Client::uploadFile(
    const std::string& token,
    const std::string& path
)
{
    std::ifstream file(
        path,
        std::ios::binary
    );

    if (!file.is_open())
    {
        std::cout
            << "Cannot open file\n";

        return;
    }

    std::string filename =
        std::filesystem
        ::path(path)
        .filename()
        .string();

    file.seekg(
        0,
        std::ios::end
    );

    int filesize =
        file.tellg();

    file.seekg(
        0,
        std::ios::beg
    );

    std::string command =
        "UPLOAD "
        + token
        + " "
        + filename
        + " "
        + std::to_string(
            filesize
        );

    send(
        sock,
        command.c_str(),
        command.size(),
        0
    );

    char buffer[1024] = {0};

    recv(
        sock,
        buffer,
        sizeof(buffer),
        0
    );

    std::string response =
        buffer;

    if (
        response
        != "READY_UPLOAD"
    )
    {
        std::cout
            << response
            << "\n";

        return;
    }

    std::vector<char> data(
        filesize
    );

    file.read(
        data.data(),
        filesize
    );

    send(
        sock,
        data.data(),
        filesize,
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