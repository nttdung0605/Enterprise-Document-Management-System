#include "client.h"

#include <iostream>
#include <string>

#include <winsock2.h>
#include <ws2tcpip.h>

#include <fstream>
#include <filesystem>

#include <sstream>
#include <vector>
#include <algorithm>

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

        if (
            command.rfind(
                "DOWNLOAD_FILE",
                0
            ) == 0
        )
        {
            std::stringstream ss(
                command
            );
        
            std::string cmd;
            std::string token;
            int versionId;
        
            ss
            >> cmd
            >> token
            >> versionId;
        
            std::string path;
        
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
        
            downloadFile(
                token,
                versionId,
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

void Client::downloadFile(
    const std::string& token,
    int versionId,
    const std::string& saveFolder
)
{
    std::string command =
        "DOWNLOAD "
        + token
        + " "
        + std::to_string(
            versionId
        );

    send(
        sock,
        command.c_str(),
        command.size(),
        0
    );

    char buffer[4096] = {0};

    int hdrBytes = recv(
        sock,
        buffer,
        sizeof(buffer),
        0
    );

    if (hdrBytes <= 0)
    {
        std::cout << "No response from server\n";
        return;
    }

    std::string response(buffer, hdrBytes);

    if (response.find("READY_DOWNLOAD") != 0)
    {
        std::cout << response << "\n";
        return;
    }

    std::stringstream ss(response);

    std::string status;
    std::string filename;
    int filesize;

    ss >> status >> filename >> filesize;

    std::string savePath = saveFolder + "\\" + filename;

    std::ofstream file(savePath, std::ios::binary);

    int received = 0;
    std::string leftoverMsg;

    while (received < filesize)
    {
        int bytes = recv(sock, buffer, sizeof(buffer), 0);

        if (bytes <= 0)
            break;

        int toWrite = bytes;

        if (received + toWrite > filesize)
        {
            toWrite = filesize - received;
            leftoverMsg.assign(buffer + toWrite, bytes - toWrite);
        }

        file.write(buffer, toWrite);
        received += toWrite;
    }

    file.close();

    std::string finalResponse;

    if (!leftoverMsg.empty())
    {
        finalResponse = leftoverMsg;
    }
    else
    {
        memset(buffer, 0, sizeof(buffer));
        int r = recv(sock, buffer, sizeof(buffer), 0);
        if (r > 0)
            finalResponse.assign(buffer, r);
    }

    while (!finalResponse.empty() && (finalResponse.back() == '\0' || finalResponse.back() == '\n' || finalResponse.back() == '\r'))
        finalResponse.pop_back();

    std::cout << finalResponse << "\n";
    std::cout << "Saved to: " << savePath << "\n";
}