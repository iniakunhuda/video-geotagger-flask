<template>
    <div class="space-y-6">
        <div class="card">
            <h1 class="text-2xl font-bold text-gray-900 mb-6">
                Read Image Metadata
            </h1>

            <!-- Upload Form -->
            <form @submit.prevent="handleSubmit" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700"
                        >Image File</label
                    >
                    <input
                        type="file"
                        accept="image/jpeg,image/jpg,image/png"
                        @change="handleFileChange"
                        class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                    <p class="mt-1 text-sm text-gray-500">
                        Supported formats: JPEG, JPG, PNG
                    </p>
                </div>

                <div class="flex justify-between items-center pt-4">
                    <div
                        class="block text-sm font-medium text-gray-700"
                        v-if="selectedFile"
                    >
                        <p class="mb-2">Selected file</p>
                        <p class="text-gray-500 font-normal">
                            {{ selectedFile.name }} ({{
                                formatFileSize(selectedFile.size)
                            }})
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
                            <span>{{
                                isLoading
                                    ? "Reading metadata..."
                                    : "Read Metadata"
                            }}</span>
                        </div>
                    </button>
                </div>
            </form>
        </div>

        <!-- Results Section -->
        <div v-if="metadata" class="card">
            <div class="flex flex-col sm:flex-row gap-6">
                <!-- Image Preview -->
                <div class="w-full sm:w-1/3">
                    <h3 class="text-lg font-semibold mb-4">Image Preview</h3>
                    <img
                        :src="imagePreview"
                        alt="Selected image"
                        class="w-full rounded-lg shadow-md"
                    />
                </div>

                <!-- Metadata Display -->
                <div class="w-full sm:w-2/3 space-y-6">
                    <div>
                        <h3 class="text-lg font-semibold mb-4">
                            Image Information
                        </h3>
                        <dl
                            class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2"
                        >
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    File Type
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.file_type }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Image Size
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.image_size }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Created At
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.created_at }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Color Model
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.color_model }}
                                </dd>
                            </div>
                        </dl>
                    </div>

                    <div v-if="metadata.camera">
                        <h3 class="text-lg font-semibold mb-4">
                            Camera Information
                        </h3>
                        <dl
                            class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2"
                        >
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Make
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.camera.make }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Model
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.camera.model }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Lens
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.camera.lens }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Focal Length
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.camera.focal_length }}mm
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Aperture
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    f/{{ metadata.camera.aperture }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    ISO
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.camera.iso }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Exposure
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    1/{{
                                        Math.round(
                                            1 / metadata.camera.exposure
                                        )
                                    }}s
                                </dd>
                            </div>
                        </dl>
                    </div>

                    <div v-if="metadata.latitude && metadata.longitude">
                        <h3 class="text-lg font-semibold mb-4">
                            Location Information
                        </h3>
                        <dl
                            class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2"
                        >
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Latitude
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{
                                        formatCoordinate(
                                            metadata.latitude,
                                            "lat"
                                        )
                                    }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Longitude
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{
                                        formatCoordinate(
                                            metadata.longitude,
                                            "lon"
                                        )
                                    }}
                                </dd>
                            </div>
                            <div
                                v-if="metadata.altitude"
                                class="flex flex-col py-2"
                            >
                                <dt class="text-sm font-medium text-gray-500">
                                    Altitude
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{ metadata.altitude.toFixed(1) }}m
                                </dd>
                            </div>
                        </dl>

                        <!-- Google Maps Link -->
                        <a
                            :href="googleMapsLink"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="inline-flex items-center mt-4 text-blue-600 hover:text-blue-800"
                        >
                            <MapIcon class="w-5 mr-2" />
                            View Location on Google Maps
                        </a>
                    </div>

                    <div v-if="metadata.camera?.flash">
                        <h3 class="text-lg font-semibold mb-4">
                            Flash Information
                        </h3>
                        <dl class="grid grid-cols-1 gap-y-2">
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Flash Status
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{
                                        metadata.camera.flash.flash_fired
                                            ? "Fired"
                                            : "Did not fire"
                                    }}
                                </dd>
                            </div>
                            <div class="flex flex-col py-2">
                                <dt class="text-sm font-medium text-gray-500">
                                    Flash Mode
                                </dt>
                                <dd class="text-sm text-gray-900">
                                    {{
                                        formatFlashMode(
                                            metadata.camera.flash.flash_mode
                                        )
                                    }}
                                </dd>
                            </div>
                        </dl>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from "vue";
import axios from "axios";

import { MapIcon } from "@heroicons/vue/24/outline";

const API_URL = "http://127.0.0.1:5000";

const selectedFile = ref(null);
const isLoading = ref(false);
const metadata = ref(null);
const imagePreview = ref(null);

const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        selectedFile.value = file;
        // Create image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.value = e.target.result;
        };
        reader.readAsDataURL(file);
    }
};

const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const formatCoordinate = (coord, type) => {
    if (!Array.isArray(coord) || coord.length !== 3) return "N/A";

    const degrees = Math.abs(coord[0]);
    const minutes = Math.abs(coord[1]);
    const seconds = Math.abs(coord[2]);

    let direction = "";
    if (type === "lat") {
        direction = coord[0] >= 0 ? "N" : "S";
    } else {
        direction = coord[0] >= 0 ? "E" : "W";
    }

    return `${degrees}° ${minutes}' ${seconds.toFixed(2)}" ${direction}`;
};

const formatFlashMode = (mode) => {
    return mode
        .split("_")
        .map((word) => word.charAt(0) + word.slice(1).toLowerCase())
        .join(" ");
};

// const googleMapsLink = computed(() => {
//     if (!metadata.value?.latitude || !metadata.value?.longitude) return "#";

//     const lat =
//         metadata.value.latitude[0] +
//         metadata.value.latitude[1] / 60 +
//         metadata.value.latitude[2] / 3600;

//     const lon =
//         metadata.value.longitude[0] +
//         metadata.value.longitude[1] / 60 +
//         metadata.value.longitude[2] / 3600;

//     return `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
// });

const dmsToDecimal = (coordinates) => {
    if (!Array.isArray(coordinates) || coordinates.length !== 3) {
        return null;
    }

    const degrees = coordinates[0];
    const minutes = coordinates[1];
    const seconds = coordinates[2];

    let decimal = degrees + minutes / 60 + seconds / 3600;
    return decimal;
};

const googleMapsLink = computed(() => {
    if (!metadata.value?.latitude || !metadata.value?.longitude) return "#";

    try {
        // Convert latitude array to decimal
        const latDecimal = dmsToDecimal(metadata.value.latitude);
        // Convert longitude array to decimal
        const lonDecimal = dmsToDecimal(metadata.value.longitude);

        // Check if conversion was successful
        if (latDecimal === null || lonDecimal === null) {
            return "#";
        }

        // Apply direction (N/S, E/W)
        const finalLat =
            metadata.value.latitude_ref === "S" ? -latDecimal : latDecimal;
        const finalLon =
            metadata.value.longitude_ref === "W" ? -lonDecimal : lonDecimal;

        // Format to 7 decimal places for high precision
        const formattedLat = finalLat.toFixed(7);
        const formattedLon = finalLon.toFixed(7);

        return `https://www.google.com/maps/search/?api=1&query=${formattedLat},${formattedLon}`;
    } catch (error) {
        console.error("Error generating Google Maps link:", error);
        return "#";
    }
});

// Function to open Google Maps
const openGoogleMaps = () => {
    if (googleMapsLink.value === "#") {
        alert("Invalid coordinates in metadata");
        return;
    }

    window.open(googleMapsLink.value, "_blank");
};

const handleSubmit = async () => {
    if (!selectedFile.value) return;

    const formData = new FormData();
    formData.append("image", selectedFile.value);

    try {
        isLoading.value = true;
        const response = await axios.post(`${API_URL}/read-metadata`, formData);
        metadata.value = response.data.exif_data;
    } catch (error) {
        console.error("Error reading metadata:", error);
        alert(error.response?.data?.error || "Error reading metadata");
    } finally {
        isLoading.value = false;
    }
};
</script>
