<template>
    <div class="min-h-screen bg-gray-100">
        <nav class="bg-white shadow-sm">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between h-16">
                    <div class="flex">
                        <div class="flex-shrink-0 flex items-center">
                            <!-- <img
                                class="h-8 w-auto"
                                src="/logo.png"
                                alt="Logo"
                            /> -->
                            <strong>ITS Video Tagger</strong>
                        </div>
                        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                            <router-link
                                to="/"
                                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                active-class="border-indigo-500 text-gray-900"
                            >
                                Dashboard
                            </router-link>
                            <!-- <router-link
                                to="/video-frames"
                                class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                                active-class="border-indigo-500 text-gray-900"
                            >
                                Split Video to Frames
                            </router-link> -->
                        </div>
                    </div>
                </div>
            </div>
        </nav>

        <div class="py-10">
            <main>
                <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
                    <router-view></router-view>
                </div>
            </main>
        </div>
    </div>
</template>

<script setup>
// No additional script needed
</script>
