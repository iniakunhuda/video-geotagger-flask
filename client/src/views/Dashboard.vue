<template>
    <div class="space-y-6">
        <div class="card">
            <h1 class="text-3xl font-bold text-gray-900 mb-4">
                Welcome to Video Processing Tool
            </h1>
            <p class="text-gray-600">Choose from our available features:</p>
        </div>

        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div
                v-for="feature in features"
                :key="feature.name"
                class="card hover:shadow-lg transition-shadow duration-200"
            >
                <component
                    :is="feature.icon"
                    class="h-8 w-8 text-blue-500 mb-4"
                />
                <h2 class="text-xl font-semibold text-gray-900 mb-2">
                    {{ feature.name }}
                </h2>
                <p class="text-gray-600 mb-4">{{ feature.description }}</p>
                <router-link
                    :to="feature.path"
                    class="btn-primary inline-block"
                >
                    Explore
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    VideoCameraIcon,
    PhotoIcon,
    MapIcon,
    ChartBarIcon,
} from "@heroicons/vue/24/outline";

const features = [
    {
        name: "Split Video to Frames",
        description:
            "Extract frames from your videos with customizable intervals.",
        icon: VideoCameraIcon,
        path: "/video-frames",
    },
    {
        name: "Read Metadata Image",
        description:
            "Reading image metadata with a nice display of the EXIF data.",
        icon: PhotoIcon,
        path: "/read-metadata",
    },
    {
        name: "Write Metadata to Image",
        description: "Writing GPS metadata to image and show EXIF data.",
        icon: MapIcon,
        path: "/write-metadata",
    },
    {
        name: "Video Geotagger",
        description: "Geotagger from Video and generate image metadata",
        icon: ChartBarIcon,
        path: "/video-geotagger",
    },
];
</script>
