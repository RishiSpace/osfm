#include <iostream>
#include <string>
#include <thread>

#include "gpu_detector.cpp" // Include a utility to detect GPU types

#ifdef _WIN32
#include "capture_windows.cpp"
#else
#include "capture_linux.cpp"
#endif

#include <iostream>
#ifdef _WIN32
#include <windows.h>
#else
#include <fstream>
#endif

enum class GPUType {
    NVIDIA,
    AMD,
    INTEL,
    UNKNOWN
};

// Function to detect the primary GPU and return its type
GPUType detectPrimaryGPU() {
    #ifdef _WIN32
    // Windows-specific GPU detection logic
    DISPLAY_DEVICE dd;
    dd.cb = sizeof(dd);
    int deviceIndex = 0;
    while (EnumDisplayDevices(0, deviceIndex, &dd, 0)) {
        if (dd.StateFlags & DISPLAY_DEVICE_PRIMARY_DEVICE) {
            std::string deviceName = dd.DeviceString;
            if (deviceName.find("NVIDIA") != std::string::npos) {
                return GPUType::NVIDIA;
            } else if (deviceName.find("AMD") != std::string::npos || deviceName.find("ATI") != std::string::npos) {
                return GPUType::AMD;
            } else if (deviceName.find("Intel") != std::string::npos) {
                return GPUType::INTEL;
            }
        }
        deviceIndex++;
    }
    #else
    // Linux-specific GPU detection logic
    std::ifstream file("/proc/driver/nvidia/version");
    if (file.good()) {
        return GPUType::NVIDIA;
    }
    file.close();
    file.open("/sys/class/drm/card0/device/vendor");
    if (file.good()) {
        std::string line;
        std::getline(file, line);
        if (line.find("0x1002") != std::string::npos) {
            return GPUType::AMD;
        } else if (line.find("0x8086") != std::string::npos) {
            return GPUType::INTEL;
        }
    }
    #endif
    return GPUType::UNKNOWN;
}

// Use GPU detector to decide which encoder to use
GPUType detectedGPU = detectPrimaryGPU();
switch (detectedGPU) {
    case GPUType::NVIDIA:
        #include "encoder_nvenc.cpp"
        break;
    case GPUType::AMD:
        #include "encoder_amf.cpp"
        break;
    case GPUType::INTEL:
        #include "encoder_intel.cpp" // Assuming there's an Intel encoder available
        break;
    default:
        #include "encoder_generic.cpp" // Fallback generic encoder if GPU type is unknown
        break;
}

#include "vulkan_renderer.cpp"
#include "streamer.cpp"
#include "client.cpp"

int main() {
    int width, height, fps;
    std::cout << "Enter desired width: ";
    std::cin >> width;
    std::cout << "Enter desired height: ";
    std::cin >> height;
    std::cout << "Enter desired FPS: ";
    std::cin >> fps;

    // Initialize screen capture
    ScreenCapture capture;
    capture.init(width, height, fps);

    // Initialize Vulkan renderer
    VulkanRenderer renderer;
    renderer.init(width, height);

    // Initialize encoder
    Encoder encoder;
    encoder.init(width, height, fps);

    // Initialize streamer
    Streamer streamer;
    streamer.init();

    // Start streaming thread
    std::thread streamingThread([&]() {
        streamer.startStreaming(capture, renderer, encoder);
    });

    // Start client thread
    std::thread clientThread([&]() {
        client.startClient(streamer);
    });

    // Wait for threads to finish
    streamingThread.join();
    clientThread.join();

    return 0;
}
}