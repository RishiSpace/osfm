#include <iostream>
#include <string>
#include <thread>
#ifdef _WIN32
#include <winsock2.h>
#include "vulkan_ren.cpp"
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#endif

class Streamer {
private:
    int socket_fd;
    struct sockaddr_in server_addr;

public:
    void init(const std::string& ip, int port) {
        // Initialize streaming socket
#ifdef _WIN32
        WSADATA wsaData;
        WSAStartup(MAKEWORD(2,2), &wsaData);
#endif
        // Create a TCP socket
        socket_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (socket_fd == -1) {
            std::cerr << "Failed to create socket." << std::endl;
            exit(EXIT_FAILURE);
        }

        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        server_addr.sin_addr.s_addr = inet_addr(ip.c_str());

        // Connect to the server
        if (connect(socket_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "Connection to server failed." << std::endl;
            exit(EXIT_FAILURE);
        }
    }

    void startStreaming(ScreenCapture& capture, VulkanRenderer& renderer, Encoder& encoder) {
        while (true) {
            // Capture a frame
            void* frame;
            capture.captureFrame(&frame);

            // Render the frame using Vulkan
            renderer.renderFrame(frame);

            // Encode the frame using the encoder
            std::vector<unsigned char> encodedData;
            encoder.encodeFrame(frame, encodedData);

            // Send the encoded frame over the network
            if (send(socket_fd, encodedData.data(), encodedData.size(), 0) < 0) {
                std::cerr << "Failed to send data." << std::endl;
                break;
            }
        }
        close(socket_fd);
#ifdef _WIN32
        WSACleanup();
#endif
    }
};