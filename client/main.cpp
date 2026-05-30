#include "client.h"

int main()
{
    Client client;

    bool connected =
        client.connectToServer(
            "127.0.0.1",
            5000
        );

    if (!connected)
    {
        return 1;
    }

    client.startCLI();

    return 0;
}