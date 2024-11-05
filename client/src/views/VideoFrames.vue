<template>
    <div class="space-y-6">
        <div class="card">
            <h1 class="text-2xl font-bold text-gray-900 mb-6">
                Split Video to Frames
            </h1>

            <!-- Upload Form -->
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700"
                        >Video File (Max 2 minutes)</label
                    >
                    <input
                        type="file"
                        accept="video/*"
                        @change="handleFileChange"
                        class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                    <p class="mt-1 text-sm text-gray-500">
                        Select a video file (MP4, AVI, MOV recommended)
                    </p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700"
                            >Frame Interval (seconds)</label
                        >
                        <input
                            type="number"
                            v-model="frameInterval"
                            min="1"
                            max="30"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                        <p class="mt-1 text-sm text-gray-500">
                            Time between extracted frames (1-30 seconds)
                        </p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700"
                            >Maximum Frames</label
                        >
                        <input
                            type="number"
                            v-model="maxFrames"
                            min="1"
                            max="100"
                            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                        />
                        <p class="mt-1 text-sm text-gray-500">
                            Maximum number of frames to extract (default: 30)
                        </p>
                    </div>
                </div>

                <div class="flex justify-between items-center pt-4">
                    <div class="text-sm text-gray-500">
                        <p v-if="selectedFile">
                            Selected file: {{ selectedFile.name }}
                            <span class="ml-2"
                                >({{ formatFileSize(selectedFile.size) }})</span
                            >
                        </p>
                    </div>
                    <button
                        type="submit"
                        class="btn-primary"
                        :disabled="!selectedFile || isLoading"
                    >
                        <div class="flex items-center space-x-2">
                            <svg
                                v-if="isLoading"
                                class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                            >
                                <circle
                                    class="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    stroke-width="4"
                                ></circle>
                                <path
                                    class="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                ></path>
                            </svg>
                            <span v-if="isLoading">Processing...</span>
                            <span v-else>Process Video</span>
                        </div>
                    </button>
                </div>
            </form>
        </div>

        <!-- Results Section -->
        <div v-if="frames.length" class="card">
            <div
                class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6"
            >
                <div>
                    <h2 class="text-xl font-semibold text-gray-900">
                        Extracted Frames
                    </h2>
                    <p class="text-sm text-gray-600">
                        Total frames: {{ frames.length }} | Selected:
                        {{ selectedFrames.length }}
                    </p>
                </div>
                <div class="flex gap-2">
                    <button
                        @click="selectAllFrames"
                        class="px-4 py-2 bg-gray-100 text-gray-700 font-medium rounded-lg hover:bg-gray-200"
                    >
                        Select All
                    </button>
                    <button
                        @click="downloadSelectedFrames"
                        class="btn-primary"
                        :disabled="!selectedFrames.length"
                    >
                        {{
                            selectedFrames.length > 1
                                ? "Download Selected as ZIP"
                                : "Download Selected"
                        }}
                        ({{ selectedFrames.length }})
                    </button>
                </div>
            </div>

            <!-- Grid of frames -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                    v-for="(frame, index) in frames"
                    :key="index"
                    class="relative border rounded-lg p-2 group hover:shadow-lg transition-shadow duration-200"
                >
                    <div class="absolute top-2 left-2 z-10">
                        <input
                            type="checkbox"
                            :checked="selectedFrames.includes(frame)"
                            @change="toggleFrameSelection(frame)"
                            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                    </div>
                    <img
                        :src="frame"
                        :alt="`Frame ${index + 1}`"
                        class="w-full h-48 object-cover rounded"
                    />
                    <div class="mt-2 flex justify-between items-center px-1">
                        <p class="text-sm text-gray-600">
                            Frame {{ index + 1 }}
                        </p>
                        <button
                            @click="downloadSingleFrame(frame, index)"
                            class="text-blue-600 hover:text-blue-800 text-sm"
                        >
                            Download
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import JSZip from "jszip";

const API_URL = "http://127.0.0.1:5000";

const selectedFile = ref(null);
const frameInterval = ref(5);
const maxFrames = ref(30);
const isLoading = ref(false);
const frames = ref([]);
const selectedFrames = ref([]);

const handleFileChange = (event) => {
    selectedFile.value = event.target.files[0];
};

const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const handleSubmit = async () => {
    if (!selectedFile.value) return;

    const formData = new FormData();
    formData.append("video", selectedFile.value);
    formData.append("frame_interval", frameInterval.value);
    formData.append("max_frames", maxFrames.value);

    try {
        isLoading.value = true;
        const response = await axios.post(`${API_URL}/split-video`, formData);
        frames.value = response.data.frames || [];
        selectedFrames.value = []; // Reset selections
    } catch (error) {
        console.error("Error processing video:", error);
        alert(error.response?.data?.error || "Error processing video");
    } finally {
        isLoading.value = false;
    }
};

const toggleFrameSelection = (frame) => {
    const index = selectedFrames.value.indexOf(frame);
    if (index === -1) {
        selectedFrames.value.push(frame);
    } else {
        selectedFrames.value.splice(index, 1);
    }
};

const selectAllFrames = () => {
    if (selectedFrames.value.length === frames.value.length) {
        selectedFrames.value = [];
    } else {
        selectedFrames.value = [...frames.value];
    }
};

const downloadSingleFrame = async (frame, index) => {
    try {
        const base64Data = frame.replace(/^data:image\/\w+;base64,/, "");
        const byteCharacters = atob(base64Data);
        const byteArrays = [];

        for (let i = 0; i < byteCharacters.length; i++) {
            byteArrays.push(byteCharacters.charCodeAt(i));
        }

        const blob = new Blob([new Uint8Array(byteArrays)], {
            type: "image/jpeg",
        });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `frame_${index + 1}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
    } catch (error) {
        console.error("Error downloading frame:", error);
        alert("Error downloading frame");
    }
};

// const downloadSelectedFrames = async () => {
//     for (let [index, frame] of selectedFrames.value.entries()) {
//         try {
//             const base64Data = frame.replace(/^data:image\/\w+;base64,/, "");
//             const byteCharacters = atob(base64Data);
//             const byteArrays = [];

//             for (let i = 0; i < byteCharacters.length; i++) {
//                 byteArrays.push(byteCharacters.charCodeAt(i));
//             }

//             const blob = new Blob([new Uint8Array(byteArrays)], {
//                 type: "image/jpeg",
//             });
//             const link = document.createElement("a");
//             link.href = URL.createObjectURL(blob);
//             link.download = `frame_${index + 1}.jpg`;
//             document.body.appendChild(link);
//             link.click();
//             document.body.removeChild(link);
//             URL.revokeObjectURL(link.href);

//             // Add a small delay between downloads
//             await new Promise((resolve) => setTimeout(resolve, 100));
//         } catch (error) {
//             console.error("Error downloading frame:", error);
//         }
//     }
// };

const downloadSelectedFrames = async () => {
    // If only one frame is selected, use single download
    if (selectedFrames.value.length === 1) {
        await downloadSingleFrame(selectedFrames.value[0], 0);
        return;
    }

    try {
        isLoading.value = true;
        const zip = new JSZip();

        // Create frames folder in zip
        const framesFolder = zip.folder("frames");

        // Add each frame to the zip
        for (let [index, frame] of selectedFrames.value.entries()) {
            try {
                // Convert base64 to blob
                const base64Data = frame.replace(
                    /^data:image\/\w+;base64,/,
                    ""
                );
                const binaryString = atob(base64Data);
                const bytes = new Uint8Array(binaryString.length);

                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }

                // Add file to zip with padding in name for correct sorting
                const paddedIndex = String(index + 1).padStart(3, "0");
                framesFolder.file(`frame_${paddedIndex}.jpg`, bytes);
            } catch (error) {
                console.error(`Error processing frame ${index + 1}:`, error);
            }
        }

        // Generate zip file
        const zipContent = await zip.generateAsync(
            {
                type: "blob",
                compression: "DEFLATE",
                compressionOptions: {
                    level: 6, // Compression level (1-9)
                },
            },
            (metadata) => {
                // You could add a progress indicator here if needed
                console.log(
                    "Zip progress: ",
                    metadata.percent.toFixed(2) + "%"
                );
            }
        );

        // Download zip file
        const link = document.createElement("a");
        link.href = URL.createObjectURL(zipContent);
        link.download = `frames_${new Date()
            .toISOString()
            .slice(0, 19)
            .replace(/[:-]/g, "")}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);
    } catch (error) {
        console.error("Error creating zip file:", error);
        alert("Error creating zip file");
    } finally {
        isLoading.value = false;
    }
};
</script>
