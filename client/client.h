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

private:
    SOCKET sock;
};