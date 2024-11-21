<script setup>
import { ref, onMounted } from "vue";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import { PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import Papa from "papaparse";
import "leaflet/dist/leaflet.css";
import JSZip from "jszip";

import axios from "axios";
const API_URL = "http://127.0.0.1:5000";

const videoFile = ref(null);
const videoElement = ref(null);
const selectedVideoFile = ref(null);
const selectedCsvFile = ref(null);
const flightHistory = ref([]);
const markers = ref([]);
const customMarkers = ref([]);
const mapCenter = ref([0, 0]);
const markerInterval = ref(2);
const isLoadingCsv = ref(false);

const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const handleVideoFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        selectedVideoFile.value = file;
        videoFile.value = URL.createObjectURL(file);
    }
};

const handleCsvFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
        selectedCsvFile.value = file;
    }
};

const handleCsvSubmit = async () => {
    if (!selectedCsvFile.value) return;

    isLoadingCsv.value = true;

    try {
        await new Promise((resolve) => {
            Papa.parse(selectedCsvFile.value, {
                header: true,
                complete: (results) => {
                    const uniquePoints = new Set();
                    const flightPoints = [];

                    results.data.forEach((row) => {
                        // Convert coordinates from degE7 to decimal degrees
                        const lat = row["GLOBAL_POSITION_INT.lat"];
                        const lon = row["GLOBAL_POSITION_INT.lon"];
                        const alt = row["AHRS2.altitude"];

                        // Validate coordinates
                        if (
                            !isNaN(lat) &&
                            !isNaN(lon) &&
                            !isNaN(alt) &&
                            (lat !== "0.0" || lon !== "0.0") &&
                            (lat !== "" || lon !== "")
                        ) {
                            const pointKey = `${lat},${lon}`;
                            if (!uniquePoints.has(pointKey)) {
                                uniquePoints.add(pointKey);
                                flightPoints.push({
                                    altitude: alt,
                                    lat: lat,
                                    lng: lon,
                                    timestamp: new Date(
                                        row.timestamp
                                    ).getTime(),
                                });

                                // add to custom marker too
                                // customMarkers.value.push({
                                //     lat: Number(lat),
                                //     lng: Number(lon),
                                //     timestamp: new Date(
                                //         row.timestamp
                                //     ).getTime(),
                                //     isCustom: false,
                                // });
                            }
                        }
                    });

                    console.log(flightPoints);

                    flightPoints.sort((a, b) => a.timestamp - b.timestamp);

                    if (flightPoints.length > 0) {
                        mapCenter.value = [
                            flightPoints[0].lat,
                            flightPoints[0].lng,
                        ];
                        markers.value = flightPoints;
                        flightHistory.value = flightPoints;
                        console.log(
                            `Loaded ${flightPoints.length} unique flight points`
                        );
                    } else {
                        console.warn("No valid GPS points found in CSV");
                    }

                    resolve();
                },
                error: (error) => {
                    console.error("Error parsing CSV:", error);
                    resolve();
                },
            });
        });
    } catch (error) {
        console.error("Error processing CSV:", error);
    } finally {
        isLoadingCsv.value = false;
    }
};

const handleMapClick = (event) => {
    if (videoElement.value) {
        customMarkers.value.push({
            lat: event.latlng.lat,
            lng: event.latlng.lng,
            timestamp: videoElement.value.currentTime,
            isCustom: true,
        });
    }
};

const updateMarkers = () => {
    if (!videoElement.value || flightHistory.value.length === 0) return;

    const currentTime = videoElement.value.currentTime;
    const baseTimestamp = flightHistory.value[0].timestamp;
    const videoTimestamp = baseTimestamp + currentTime;

    // Find the closest GPS point to the current video time
    const closestPoint = flightHistory.value.reduce((prev, curr) => {
        return Math.abs(curr.timestamp - videoTimestamp) <
            Math.abs(prev.timestamp - videoTimestamp)
            ? curr
            : prev;
    });

    markers.value = [
        {
            lat: closestPoint.lat,
            lng: closestPoint.lon,
            timestamp: currentTime,
            isCustom: false,
        },
    ];
};

const removeCustomMarker = (index) => {
    customMarkers.value.splice(index, 1);
};

const formatDateFromTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toString();
};

// Clean up event listeners when component is unmounted
const cleanupVideoListeners = () => {
    if (videoElement.value) {
        videoElement.value.removeEventListener("timeupdate", updateMarkers);
    }
};

onMounted(() => {
    if (videoElement.value) {
        videoElement.value.addEventListener("timeupdate", updateMarkers);
    }
    return cleanupVideoListeners;
});

const isExporting = ref(false);
const exportedFrames = ref([]);
const frameInterval = ref(5);
const pathStats = ref(null);

const exportMarkers = async () => {
    if (!videoFile.value || !customMarkers.value.length) return;

    isExporting.value = true;
    try {
        // Create form data
        const formData = new FormData();
        formData.append("video", selectedVideoFile.value);
        formData.append("markers", JSON.stringify(customMarkers.value));
        formData.append("frames_interval", frameInterval.value.toString());

        // Send request to server
        const response = await axios.post(
            `${API_URL}/interpolate-path`,
            formData
        );

        // Store exported data
        exportedFrames.value = response.data.points;
        pathStats.value = response.data.path_stats;

        // Download the results as JSON
        const jsonContent = JSON.stringify(response.data, null, 2);
        const blob = new Blob([jsonContent], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "video-markers.json";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Error exporting markers:", error);
        alert(
            "Error exporting markers: " +
                (error.response?.data?.error || error.message)
        );
    } finally {
        isExporting.value = false;
    }
};

// const exportMarkers = async () => {
//     if (!videoFile.value || !customMarkers.value.length) return;

//     isExporting.value = true;
//     try {
//         // Create form data
//         const formData = new FormData();
//         formData.append("video", selectedVideoFile.value);
//         formData.append("markers", JSON.stringify(customMarkers.value));
//         formData.append("frames_interval", frameInterval.value.toString());

//         // Send request to server
//         const response = await axios.post(
//             `${API_URL}/interpolate-path`,
//             formData
//         );

//         // Store exported data
//         exportedFrames.value = response.data.points;
//         pathStats.value = response.data.path_stats;

//         // Create a new ZIP file
//         const zip = new JSZip();
//         const promises = [];

//         // Process each frame and add metadata
//         for (const point of exportedFrames.value) {
//             const metadata = {
//                 gps_latitude: decimalToDMS(Math.abs(point.lat)),
//                 gps_latitude_ref: point.lat >= 0 ? "N" : "S",
//                 gps_longitude: decimalToDMS(Math.abs(point.lng)),
//                 gps_longitude_ref: point.lng >= 0 ? "E" : "W",
//                 gps_altitude: point.altitude || 0,
//                 gps_altitude_ref: "ABOVE_SEA_LEVEL"
//             };

//             // Create form data for each image
//             const imageFormData = new FormData();
//             const imageBlob = await base64ToBlob(point.frame, 'image/jpeg');
//             imageFormData.append("image", imageBlob);
//             imageFormData.append("metadata", JSON.stringify(metadata));

//             // Add to promises array
//             promises.push(
//                 axios.post(`${API_URL}/write-metadata`, imageFormData)
//                     .then(response => ({
//                         image: response.data.updated_image,
//                         timestamp: point.timestamp
//                     }))
//             );
//         }

//         // Wait for all metadata writing operations to complete
//         const results = await Promise.all(promises);

//         // Add each processed image to the ZIP file
//         results.forEach((result, index) => {
//             console.log("Result", result);
//             const fileName = `frame_${result.timestamp.toFixed(2)}s.jpg`;
//             zip.file(fileName, result.image.split(',')[1], { base64: true });
//         });

//         // Generate and download the ZIP file
//         const zipBlob = await zip.generateAsync({ type: "blob" });
//         const zipUrl = URL.createObjectURL(zipBlob);
//         const link = document.createElement("a");
//         link.href = zipUrl;
//         link.download = "video-frames.zip";
//         document.body.appendChild(link);
//         link.click();
//         document.body.removeChild(link);
//         URL.revokeObjectURL(zipUrl);

//         // Also save the JSON data
//         const jsonContent = JSON.stringify(response.data, null, 2);
//         const jsonBlob = new Blob([jsonContent], { type: "application/json" });
//         const jsonUrl = URL.createObjectURL(jsonBlob);
//         const jsonLink = document.createElement("a");
//         jsonLink.href = jsonUrl;
//         jsonLink.download = "video-markers.json";
//         document.body.appendChild(jsonLink);
//         jsonLink.click();
//         document.body.removeChild(jsonLink);
//         URL.revokeObjectURL(jsonUrl);

//     } catch (error) {
//         console.error("Error exporting markers:", error);
//         alert(
//             "Error exporting markers: " +
//             (error.response?.data?.error || error.message)
//         );
//     } finally {
//         isExporting.value = false;
//     }
// };

// Add helper functions for coordinate conversion
const decimalToDMS = (decimal) => {
    const degrees = Math.floor(decimal);
    const minutesDecimal = (decimal - degrees) * 60;
    const minutes = Math.floor(minutesDecimal);
    const seconds = ((minutesDecimal - minutes) * 60).toFixed(2);

    return [degrees, minutes, parseFloat(seconds)];
};

const base64ToBlob = async (base64Data, contentType) => {
    try {
        const response = await fetch(base64Data);
        const blob = await response.blob();
        return new Blob([blob], { type: contentType });
    } catch (error) {
        console.error("Error converting base64 to blob:", error);
        throw error;
    }
};
</script>

<template>
    <!-- Template remains the same as previous version -->
    <div class="container mx-auto p-4">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- Video Upload Card -->
            <div class="card">
                <h1 class="text-2xl font-bold text-gray-900 mb-6">
                    Video Upload
                </h1>

                <form class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700"
                            >Video File</label
                        >
                        <input
                            type="file"
                            accept="video/*"
                            @change="handleVideoFileChange"
                            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        <p class="mt-1 text-sm text-gray-500">
                            Supported formats: MP4, WebM, Ogg
                        </p>
                    </div>

                    <div class="flex justify-between items-center pt-4">
                        <div
                            class="block text-sm font-medium text-gray-700"
                            v-if="selectedVideoFile"
                        >
                            <p class="mb-2">Selected file</p>
                            <p class="text-gray-500 font-normal">
                                {{ selectedVideoFile.name }} ({{
                                    formatFileSize(selectedVideoFile.size)
                                }})
                            </p>
                        </div>
                    </div>
                </form>

                <div class="mt-6" v-if="videoFile">
                    <video
                        ref="videoElement"
                        :src="videoFile"
                        controls
                        class="w-full rounded-lg"
                    ></video>
                </div>
            </div>

            <!-- Flight History Upload Card -->
            <div class="card">
                <h1 class="text-2xl font-bold text-gray-900 mb-6">
                    Flight History Upload
                </h1>

                <form @submit.prevent="handleCsvSubmit" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700"
                            >CSV File</label
                        >
                        <input
                            type="file"
                            accept=".csv"
                            @change="handleCsvFileChange"
                            class="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        <p class="mt-1 text-sm text-gray-500">
                            Upload your flight history CSV file
                        </p>
                    </div>

                    <!-- Marker Interval Control -->
                    <div class="mt-14 pt-5">
                        <div class="space-y-2">
                            <label
                                class="block text-sm font-medium text-gray-700"
                            >
                                Frame Interval (seconds)
                            </label>
                            <div class="flex items-center space-x-2">
                                <input
                                    v-model="frameInterval"
                                    type="number"
                                    min="1"
                                    max="60"
                                    class="block w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                    placeholder="1"
                                />
                                <span class="text-sm text-gray-500">
                                    Extract a frame every
                                    {{ frameInterval }} seconds
                                </span>
                            </div>
                            <p class="text-xs text-gray-500">
                                Recommended: 1-5 seconds for detailed paths,
                                5-30 seconds for longer videos
                            </p>
                        </div>
                    </div>

                    <div class="flex justify-between items-center pt-4">
                        <div
                            class="block text-sm font-medium text-gray-700"
                            v-if="selectedCsvFile"
                        >
                            <p class="mb-2">Selected file</p>
                            <p class="text-gray-500 font-normal">
                                {{ selectedCsvFile.name }} ({{
                                    formatFileSize(selectedCsvFile.size)
                                }})
                            </p>
                        </div>
                        <button
                            type="submit"
                            class="btn-primary"
                            :disabled="!selectedCsvFile || isLoadingCsv"
                        >
                            <div class="flex items-center space-x-2">
                                <svg
                                    v-if="isLoadingCsv"
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
                                    isLoadingCsv
                                        ? "Processing..."
                                        : "Process CSV"
                                }}</span>
                            </div>
                        </button>
                    </div>
                </form>

                <!-- Flight Stats -->
                <div v-if="flightHistory.length > 0" class="mt-6">
                    <h3 class="text-lg font-medium text-gray-900 mb-2">
                        Flight Statistics
                    </h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <p class="text-sm text-gray-600">
                            Total GPS points: {{ flightHistory.length }}
                        </p>
                        <p class="text-sm text-gray-600">
                            Time range:
                            {{
                                (
                                    (flightHistory[flightHistory.length - 1]
                                        .timestamp -
                                        flightHistory[0].timestamp) /
                                    1000 /
                                    60
                                ).toFixed(2)
                            }}
                            minutes
                        </p>
                    </div>
                </div>

                <!-- Custom Markers List -->
                <div v-if="customMarkers.length > 0" class="mt-6">
                    <h3 class="text-lg font-medium text-gray-900 mb-4">
                        Custom Markers
                    </h3>
                    <button
                        @click="exportMarkers"
                        class="btn-primary"
                        :disabled="isExporting"
                    >
                        <div class="flex items-center space-x-2">
                            <svg
                                v-if="isExporting"
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
                                isExporting ? "Exporting..." : "Export Markers"
                            }}</span>
                        </div>
                    </button>
                    <ul class="space-y-2 h-96 overflow-y-auto">
                        <li
                            v-for="(marker, index) in customMarkers"
                            :key="index"
                            class="flex items-center justify-between bg-gray-50 p-3 rounded-lg"
                        >
                            <span class="text-sm text-gray-700">
                                {{ marker.timestamp.toFixed(2) }}s - [{{
                                    marker.lat.toFixed(6)
                                }}, {{ marker.lng.toFixed(6) }}]
                            </span>
                            <button
                                @click="removeCustomMarker(index)"
                                class="text-red-500 hover:text-red-700"
                            >
                                <TrashIcon class="h-5 w-5" />
                            </button>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Map Card -->
            <div class="card lg:col-span-2">
                <h1 class="text-2xl font-bold text-gray-900 mb-6">Map View</h1>
                <!-- {{ markers }} -->

                <div class="h-[600px] rounded-lg overflow-hidden">
                    <l-map
                        v-if="mapCenter[0] !== 0"
                        :center="mapCenter"
                        :zoom="18"
                        :use-global-leaflet="false"
                        class="h-full w-full"
                        @click="handleMapClick"
                    >
                        <l-tile-layer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <l-marker
                            v-for="(marker, index) in markers"
                            :key="'auto-' + index"
                            :lat-lng="[marker.lat, marker.lng]"
                        >
                            <l-popup>
                                <div class="text-sm">
                                    <p style="margin: 0">
                                        <b>Latitude:</b> {{ marker.lat }}°
                                    </p>
                                    <p style="margin: 0">
                                        <b>Longitude:</b> {{ marker.lng }}°
                                    </p>
                                    <p style="margin: 0">
                                        <b>Time:</b>
                                        {{
                                            formatDateFromTimestamp(
                                                marker.timestamp
                                            )
                                        }}
                                    </p>
                                </div>
                            </l-popup>
                        </l-marker>
                        <l-marker
                            v-for="(marker, index) in customMarkers"
                            :key="'custom-' + index"
                            :lat-lng="[marker.lat, marker.lng]"
                        />
                    </l-map>
                </div>
            </div>
        </div>

        <!-- Show exported frames if available -->
        <div v-if="exportedFrames.length > 0" class="mt-6 card">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
                Interpolated Path Frames
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <div
                    v-for="(point, index) in exportedFrames"
                    :key="index"
                    class="relative bg-white rounded-lg shadow-sm overflow-hidden"
                >
                    <img
                        :src="point.frame"
                        :alt="`Frame at ${point.timestamp}s`"
                        class="w-full h-48 object-cover"
                    />
                    <div
                        class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-2"
                    >
                        {{ point.timestamp.toFixed(2) }}s
                        <br />
                        [{{ point.lat.toFixed(6) }}, {{ point.lng.toFixed(6) }}]
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.card {
    @apply bg-white rounded-lg shadow-sm p-6;
}

.btn-primary {
    @apply inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed;
}
</style>
