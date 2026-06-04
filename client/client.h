#pragma once

#include <string>
#include <winsock2.h>

class Client
{
public:
    bool connectToServer(
        const std::string& ip,
        int port
    );

    void sendMessage(
        const std::string& message
    );

    void startCLI();

    void uploadFile(
        const std::string& token,
        const std::string& path
    );

    void downloadFile(
        const std::string& token,
        int versionId,
        const std::string& saveFolder
    );

    std::string calculateSHA256(
        const std::string& filepath
    );

private:
    SOCKET sock;
};