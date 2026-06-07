import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import 'preline';

Alpine.plugin(persist)

window.Alpine = Alpine

Alpine.start()