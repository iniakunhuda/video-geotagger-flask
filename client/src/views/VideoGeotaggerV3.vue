<script setup>
import { ref, onMounted } from "vue";
import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
import { PlusIcon, TrashIcon } from "@heroicons/vue/24/outline";
import Papa from "papaparse";
import "leaflet/dist/leaflet.css";
import JSZip from "jszip";
import piexif from "piexifjs";

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

const isProcessCsvClicked = ref(false);
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
    isProcessCsvClicked.value = true;

    try {
        await new Promise((resolve) => {
            Papa.parse(selectedCsvFile.value, {
                header: true,
                complete: (results) => {
                    const uniquePoints = new Set();
                    const flightPoints = [];
                    console.log(results.data);

                    results.data.forEach((row) => {
                        // Extract coordinates from the new format
                        console.log("row", row);
                        const lat = parseFloat(row.latitude);
                        const lon = parseFloat(row.longitude);
                        const alt = parseFloat(row["altitude(feet)"]);
                        const timestamp = parseFloat(row["time(millisecond)"]);
                        const datetime = row["datetime(utc)"];

                        // Validate coordinates
                        if (
                            lat &&
                            lon &&
                            !isNaN(lat) &&
                            !isNaN(lon) &&
                            datetime
                        ) {
                            const pointKey = `${lat},${lon}`;
                            if (!uniquePoints.has(pointKey)) {
                                uniquePoints.add(pointKey);
                                flightPoints.push({
                                    altitude: alt,
                                    lat: lat,
                                    lng: lon,
                                    timestamp: timestamp, // Using milliseconds timestamp
                                    datetime: datetime,
                                    speed: parseFloat(row["speed(mph)"]),
                                    heading: parseFloat(
                                        row["compass_heading(degrees)"]
                                    ),
                                    pitch: parseFloat(row["pitch(degrees)"]),
                                    roll: parseFloat(row["roll(degrees)"]),
                                    batteryPercent: parseFloat(
                                        row["battery_percent"]
                                    ),
                                    state: row.flycState,
                                });
                            }
                        }
                    });

                    console.log("Processed flight points:", flightPoints);

                    // Sort points by timestamp
                    flightPoints.sort((a, b) => a.timestamp - b.timestamp);

                    if (flightPoints.length > 0) {
                        mapCenter.value = [
                            flightPoints[0].lat,
                            flightPoints[0].lng,
                        ];
                        // Store all flight points for history
                        flightHistory.value = flightPoints;

                        // Limit markers to 100 evenly distributed points
                        if (flightPoints.length > 100) {
                            const step = Math.floor(flightPoints.length / 100);
                            markers.value = flightPoints
                                .filter((_, index) => index % step === 0)
                                .slice(0, 100);
                        } else {
                            markers.value = flightPoints;
                        }
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
        isProcessCsvClicked.value = false;
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
    if (!videoFile.value || !selectedCsvFile.value) return;

    isExporting.value = true;
    try {
        // Create form data
        const formData = new FormData();
        formData.append("video", selectedVideoFile.value);
        formData.append("csv", selectedCsvFile.value);
        formData.append("frame_interval", frameInterval.value.toString());

        // Send request to server
        const response = await axios.post(
            `${API_URL}/geotagger-video-test`,
            formData
        );

        // Store exported data
        exportedFrames.value = response.data.saved_frames;

    } catch (error) {
        console.error("Error exporting frames:", error);
        alert(
            "Error exporting frames: " +
                (error.response?.data?.error || error.message)
        );
    } finally {
        isExporting.value = false;
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
                    </div>
                    <div class="flex items-center pt-0 gap-x-4">
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
                        <button
                            @click="exportMarkers"
                            type="button"
                            class="btn-primary"
                            :disabled="!(flightHistory.length > 0)"
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
                                    isExporting
                                        ? "Exporting..."
                                        : "Export Markers"
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
                <h1 class="text-2xl font-bold text-gray-900">Map View</h1>
                <p class="text-gray-400">Maximum visualize 100 points</p>

                <div class="h-[600px] rounded-lg overflow-hidden mt-6">
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
                                        <b>Time:</b> {{ marker.datetime }}
                                    </p>
                                    <p style="margin: 0">
                                        <b>Latitude:</b>
                                        {{ marker.lat.toFixed(6) }}°
                                    </p>
                                    <p style="margin: 0">
                                        <b>Longitude:</b>
                                        {{ marker.lng.toFixed(6) }}°
                                    </p>
                                    <p style="margin: 0">
                                        <b>Altitude:</b>
                                        {{ marker.altitude.toFixed(1) }} ft
                                    </p>
                                    <p style="margin: 0">
                                        <b>Speed:</b>
                                        {{ marker.speed.toFixed(1) }} mph
                                    </p>
                                    <p style="margin: 0">
                                        <b>Heading:</b>
                                        {{ marker.heading.toFixed(1) }}°
                                    </p>
                                    <p style="margin: 0">
                                        <b>Battery:</b>
                                        {{ marker.batteryPercent }}%
                                    </p>
                                    <p style="margin: 0">
                                        <b>State:</b> {{ marker.state }}
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
                Captured Frames
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <div
                    v-for="(frame, index) in exportedFrames"
                    :key="index"
                    class="relative bg-white rounded-lg shadow-sm overflow-hidden"
                >
                    <img
                        :src="`${API_URL}/${frame.path}`"
                        :alt="`Frame at ${frame.timestamp}`"
                        class="w-full h-48 object-cover"
                    />
                    <div
                        class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-2"
                    >
                        <div>
                            {{ new Date(frame.timestamp).toLocaleString() }}
                        </div>
                        <div>
                            Lat: {{ frame.telemetry.latitude.toFixed(6) }}
                        </div>
                        <div>
                            Lng: {{ frame.telemetry.longitude.toFixed(6) }}
                        </div>
                        <div>
                            Alt: {{ frame.telemetry.altitude.toFixed(1) }}m
                        </div>
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
