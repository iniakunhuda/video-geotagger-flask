import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import VideoFrames from '../views/VideoFrames.vue'
import ReadMetadataImage from '../views/ReadMetadataImage.vue'
import WriteMetadataImage from '../views/WriteMetadataImage.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'Dashboard',
            component: Dashboard
        },
        {
            path: '/video-frames',
            name: 'VideoFrames',
            component: VideoFrames
        },
        {
            path: '/read-metadata',
            name: 'ReadMetadataImage',
            component: ReadMetadataImage
        },
        {
            path: '/write-metadata',
            name: 'WriteMetadataImage',
            component: WriteMetadataImage
        }
    ]
})

export default router