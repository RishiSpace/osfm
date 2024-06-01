#include <iostream>
#include <string>
#include <thread>
#include <socket.h> // for socket programming

class Client {
public:
    void init() {
        //void init() {
        // Initialize client socket
        // Create a TCP or UDP socket
    }

    void startClient(Streamer streamer) {
        while (true) {
            // Receive an encoded frame from the streamer
            // Use the socket to receive the encoded frame

            // Decode the frame using a compatible decoder
            // NVIDIA NVDEC, AMD UVD, or Intel's Media SDK

            // Render the decoded frame on the client machine
            // Use a rendering library such as OpenGL, DirectX, or Vulkan
        }
    }
};