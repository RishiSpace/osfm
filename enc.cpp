#include <nvenc.h> // for NVIDIA NVENC
#include <amf.h> // for AMD AMF
#include <mfx.h> // for Intel's Encoder

class Encoder {
public:
    void init() {
        // Initialize encoder library
#ifdef USE_NVENC
        nvenc_create_context(&nvencContext);
#elif defined(USE_AMF)
        amf_create_context(&amfContext);
#elif defined(USE_MFX)
        mfx_create_context(&mfxContext);
#endif
    }

    void encodeFrame(void* frame) {
        // Encode a single frame using the encoder library
#ifdef USE_NVENC
        nvenc_encode_frame(nvencContext, frame);
#elif defined(USE_AMF)
        amf_encode_frame(amfContext, frame);
#elif defined(USE_MFX)
        mfx_encode_frame(mfxContext, frame);
#endif
    }

private:
#ifdef USE_NVENC
    NVENCContext* nvencContext;
#elif defined(USE_AMF)
    AMFContext* amfContext;
#elif defined(USE_MFX)
    MFXContext* mfxContext;
#endif
};