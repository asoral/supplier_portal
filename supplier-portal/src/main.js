import { createApp, reactive } from 'vue'
import './style.css'
import App from './App.vue'

import router from './router';
import resourceManager from "../../../doppio/libs/resourceManager";
import call from "../../../doppio/libs/controllers/call";
import socket from "../../../doppio/libs/controllers/socket";
import Auth from "../../../doppio/libs/controllers/auth";

const app = createApp(App);
const auth = reactive(new Auth());

app.use(router);
app.use(resourceManager);

app.provide("$auth", auth);
app.provide("$call", call);
app.provide("$socket", socket);


createApp(App).mount('#app')
