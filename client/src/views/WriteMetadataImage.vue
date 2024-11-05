<template>
    <div class="space-y-6">
        <div class="card">
            <h1 class="text-2xl font-bold text-gray-900 mb-6">
                Write GPS Metadata to Image
            </h1>

            <!-- Upload Form -->
            <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- Image Upload -->
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

                <!-- GPS Coordinates Input -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Latitude -->
                    <div>
                        <h3 class="text-sm font-medium text-gray-700 mb-3">
                            Latitude
                        </h3>
                        <div class="grid grid-cols-4 gap-2">
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Degrees</label
                                >
                                <input
                                    v-model.number="latitude.degrees"
                                    type="number"
                                    min="0"
                                    max="90"
                                    step="any"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Minutes</label
                                >
                                <input
                                    v-model.number="latitude.minutes"
                                    type="number"
                                    min="0"
                                    max="59"
                                    step="any"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Seconds</label
                                >
                                <input
                                    v-model.number="latitude.seconds"
                                    type="number"
                                    min="0"
                                    max="59.99"
                                    step="0.01"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Direction</label
                                >
                                <select
                                    v-model="latitude.ref"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                >
                                    <option value="N">N</option>
                                    <option value="S">S</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Longitude -->
                    <div>
                        <h3 class="text-sm font-medium text-gray-700 mb-3">
                            Longitude
                        </h3>
                        <div class="grid grid-cols-4 gap-2">
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Degrees</label
                                >
                                <input
                                    v-model.number="longitude.degrees"
                                    type="number"
                                    min="0"
                                    max="180"
                                    step="any"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Minutes</label
                                >
                                <input
                                    v-model.number="longitude.minutes"
                                    type="number"
                                    min="0"
                                    max="59"
                                    step="any"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Seconds</label
                                >
                                <input
                                    v-model.number="longitude.seconds"
                                    type="number"
                                    min="0"
                                    max="59.99"
                                    step="0.01"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-1">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Direction</label
                                >
                                <select
                                    v-model="longitude.ref"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                >
                                    <option value="E">E</option>
                                    <option value="W">W</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <!-- Altitude -->
                    <div>
                        <h3 class="text-sm font-medium text-gray-700 mb-3">
                            Altitude
                        </h3>
                        <div class="grid grid-cols-4 gap-2">
                            <div class="col-span-2">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Height (meters)</label
                                >
                                <input
                                    v-model.number="altitude.value"
                                    type="number"
                                    step="0.001"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                />
                            </div>
                            <div class="col-span-2">
                                <label class="block text-xs text-gray-500 mb-1"
                                    >Reference</label
                                >
                                <select
                                    v-model="altitude.ref"
                                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                >
                                    <option value="ABOVE_SEA_LEVEL">
                                        Above Sea Level
                                    </option>
                                    <option value="BELOW_SEA_LEVEL">
                                        Below Sea Level
                                    </option>
                                </select>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex justify-between items-center pt-4">
                    <div class="space-y-1">
                        <div class="text-sm text-gray-500" v-if="selectedFile">
                            <p>
                                Selected file: {{ selectedFile.name }} ({{
                                    formatFileSize(selectedFile.size)
                                }})
                            </p>
                        </div>
                        <div v-if="imagePreview" class="max-w-xs">
                            <img
                                :src="imagePreview"
                                alt="Preview"
                                class="h-32 object-cover rounded-lg"
                            />
                        </div>
                    </div>

                    <div class="flex gap-3">
                        <button
                            type="button"
                            @click="useCurrentLocation"
                            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                class="h-5 w-5 mr-2 text-gray-400"
                                viewBox="0 0 20 20"
                                fill="currentColor"
                            >
                                <path
                                    fill-rule="evenodd"
                                    d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
                                    clip-rule="evenodd"
                                />
                            </svg>
                            Use Current Location
                        </button>

                        <button
                            type="submit"
                            class="btn-primary"
                            :disabled="
                                !selectedFile ||
                                isLoading ||
                                !isValidCoordinates
                            "
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
                                        ? "Writing metadata..."
                                        : "Write Metadata"
                                }}</span>
                            </div>
                        </button>
                    </div>
                </div>
            </form>
        </div>

        <!-- Map Section -->
        <div class="card">
            <h3 class="text-lg font-medium text-gray-900 mb-4">
                Select Location from Map
            </h3>
            <div class="relative">
                <!-- Search box -->
                <div
                    class="absolute top-2 right-2 w-5/6 z-[1000] bg-white rounded-lg shadow-lg"
                >
                    <div class="flex items-center p-2">
                        <input
                            v-model="searchQuery"
                            @keyup.enter="searchLocation"
                            type="text"
                            placeholder="Search location..."
                            class="flex-1 px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                            @click="searchLocation"
                            class="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            Search
                        </button>
                    </div>
                    <!-- Search results -->
                    <div
                        v-if="searchResults.length"
                        class="border-t max-h-48 overflow-y-auto"
                    >
                        <button
                            v-for="result in searchResults"
                            :key="result.place_id"
                            @click="selectSearchResult(result)"
                            class="w-full px-4 py-2 text-left hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
                        >
                            {{ result.display_name }}
                        </button>
                    </div>
                </div>

                <!-- Map container -->
                <div class="h-[400px] rounded-lg overflow-hidden">
                    <l-map
                        ref="map"
                        v-model:zoom="zoom"
                        v-model:center="center"
                        :use-global-leaflet="false"
                        @click="handleMapClick"
                    >
                        <l-tile-layer
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            layer-type="base"
                            name="OpenStreetMap"
                        />
                        <l-marker
                            v-if="markerPosition"
                            :lat-lng="markerPosition"
                            draggable
                            @moveend="updateMarkerPosition"
                        />
                    </l-map>
                </div>
            </div>
        </div>

        <!-- Results Card -->
        <div v-if="result" class="card">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">
                Updated Metadata
            </h2>
            <pre class="bg-gray-50 p-4 rounded-lg overflow-auto text-sm">{{
                JSON.stringify(result, null, 2)
            }}</pre>

            <!-- Download Button -->
            <div class="mt-4 flex justify-end">
                <a
                    :href="downloadUrl"
                    download="image_with_gps.jpg"
                    class="btn-primary"
                    v-if="downloadUrl"
                >
                    Download Updated Image
                </a>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LMarker } from "@vue-leaflet/vue-leaflet";

const API_URL = "http://127.0.0.1:5000";

const selectedFile = ref(null);
const imagePreview = ref(null);
const isLoading = ref(false);
const result = ref(null);
const downloadUrl = ref(null);

const latitude = ref({
    degrees: 0,
    minutes: 0,
    seconds: 0,
    ref: "N",
});

const longitude = ref({
    degrees: 0,
    minutes: 0,
    seconds: 0,
    ref: "E",
});

const altitude = ref({
    value: 0,
    ref: "ABOVE_SEA_LEVEL",
});

const map = ref(null);
const zoom = ref(13);
const center = ref([0, 0]);
const markerPosition = ref(null);
const searchQuery = ref("");
const searchResults = ref([]);

// Initialize map with user's location
onMounted(() => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                center.value = [latitude, longitude];
                markerPosition.value = [latitude, longitude];
                updateCoordinatesFromDecimal(latitude, longitude);
            },
            () => {
                // Default to a central location if geolocation fails
                center.value = [0, 0];
            }
        );
    }
});

const handleMapClick = (event) => {
    const { lat, lng } = event.latlng;
    markerPosition.value = [lat, lng];
    // updateCoordinatesFromDecimal(lat, lng);
    updateLocationData(lat, lng);
};

const updateMarkerPosition = (event) => {
    const { lat, lng } = event.target.getLatLng();
    markerPosition.value = [lat, lng];
    // updateCoordinatesFromDecimal(lat, lng);
    updateLocationData(lat, lng);
};

const updateLocationData = (lat, lng, newZoom = null) => {
    markerPosition.value = [lat, lng];
    center.value = [lat, lng];
    if (newZoom !== null) {
        zoom.value = newZoom;
    }
    updateCoordinatesFromDecimal(lat, lng);
};

const updateCoordinatesFromDecimal = (lat, lng) => {
    // Update latitude
    const latDMS = decimalToDMS(Math.abs(lat));
    latitude.value = {
        ...latDMS,
        ref: lat >= 0 ? "N" : "S",
    };

    // Update longitude
    const lngDMS = decimalToDMS(Math.abs(lng));
    longitude.value = {
        ...lngDMS,
        ref: lng >= 0 ? "E" : "W",
    };
};

// Search location using Nominatim API
const searchLocation = async () => {
    if (!searchQuery.value) return;

    try {
        const response = await axios.get(
            `https://nominatim.openstreetmap.org/search`,
            {
                params: {
                    q: searchQuery.value,
                    format: "json",
                    limit: 5,
                },
            }
        );
        searchResults.value = response.data;
    } catch (error) {
        console.error("Error searching location:", error);
        alert("Error searching location");
    }
};

const selectSearchResult = (result) => {
    const lat = parseFloat(result.lat);
    const lng = parseFloat(result.lon);

    center.value = [lat, lng];
    markerPosition.value = [lat, lng];
    updateCoordinatesFromDecimal(lat, lng);
    searchResults.value = [];
    searchQuery.value = "";
    zoom.value = 15;
};

const isValidCoordinates = computed(() => {
    const latValid =
        latitude.value.degrees >= 0 &&
        latitude.value.degrees <= 90 &&
        latitude.value.minutes >= 0 &&
        latitude.value.minutes < 60 &&
        latitude.value.seconds >= 0 &&
        latitude.value.seconds < 60;

    const lonValid =
        longitude.value.degrees >= 0 &&
        longitude.value.degrees <= 180 &&
        longitude.value.minutes >= 0 &&
        longitude.value.minutes < 60 &&
        longitude.value.seconds >= 0 &&
        longitude.value.seconds < 60;

    return latValid && lonValid && selectedFile.value;
});

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

const useCurrentLocation = () => {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const alt = position.coords.altitude;

            // Update map and coordinates
            updateLocationData(lat, lon, 16); // Zoom level 16 for closer view

            // Convert decimal degrees to DMS
            latitude.value = decimalToDMS(Math.abs(lat));
            latitude.value.ref = lat >= 0 ? "N" : "S";

            longitude.value = decimalToDMS(Math.abs(lon));
            longitude.value.ref = lon >= 0 ? "E" : "W";

            if (alt !== null) {
                altitude.value.value = alt;
            }
        },
        (error) => {
            alert(`Error getting location: ${error.message}`);
        }
    );
};

const decimalToDMS = (decimal) => {
    const degrees = Math.floor(decimal);
    const minutesDecimal = (decimal - degrees) * 60;
    const minutes = Math.floor(minutesDecimal);
    const seconds = ((minutesDecimal - minutes) * 60).toFixed(2);

    return {
        degrees,
        minutes,
        seconds: parseFloat(seconds),
    };
};

const handleSubmit = async () => {
    if (!selectedFile.value || !isValidCoordinates.value) return;

    const metadata = {
        gps_latitude: [
            latitude.value.degrees,
            latitude.value.minutes,
            latitude.value.seconds,
        ],
        gps_latitude_ref: latitude.value.ref,
        gps_longitude: [
            longitude.value.degrees,
            longitude.value.minutes,
            longitude.value.seconds,
        ],
        gps_longitude_ref: longitude.value.ref,
        gps_altitude: altitude.value.value,
        gps_altitude_ref: altitude.value.ref,
    };

    const formData = new FormData();
    formData.append("image", selectedFile.value);
    formData.append("metadata", JSON.stringify(metadata));

    try {
        isLoading.value = true;
        const response = await axios.post(
            `${API_URL}/write-metadata`,
            formData
        );
        result.value = response.data.exif_data;

        // Create download URL for the updated image
        if (response.data.updated_image) {
            const blob = base64ToBlob(
                response.data.updated_image,
                selectedFile.value.type
            );
            downloadUrl.value = URL.createObjectURL(blob);
        }
    } catch (error) {
        console.error("Error writing metadata:", error);
        alert(error.response?.data?.error || "Error writing metadata");
    } finally {
        isLoading.value = false;
    }
};

const base64ToBlob = (base64Data, contentType) => {
    try {
        const byteCharacters = atob(base64Data.split(",")[1]);
        const byteArrays = [];

        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);

            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }

            byteArrays.push(new Uint8Array(byteNumbers));
        }

        return new Blob(byteArrays, { type: contentType });
    } catch (error) {
        console.error("Error converting base64 to blob:", error);
        return null;
    }
};
</script>

<style scoped>
input[type="number"] {
    -moz-appearance: textfield;
}

input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
</style>
