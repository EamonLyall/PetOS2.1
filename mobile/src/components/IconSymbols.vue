<template>
  <svg width="0" height="0" style="position: absolute" aria-hidden="true">
    <defs>
      <symbol id="i-paw" viewBox="0 0 24 24"><ellipse cx="6.6" cy="9.4" rx="2.1" ry="2.7" transform="rotate(-18 6.6 9.4)" /><ellipse cx="10.4" cy="5.6" rx="2" ry="2.6" transform="rotate(-6 10.4 5.6)" /><ellipse cx="14.9" cy="5.6" rx="2" ry="2.6" transform="rotate(8 14.9 5.6)" /><ellipse cx="18.6" cy="9.4" rx="2.1" ry="2.7" transform="rotate(18 18.6 9.4)" /><path d="M12.4 11.2c3.2 0 5.6 2.3 5.6 5.1 0 2.2-1.7 3.4-3.6 3.4-1.1 0-1.6-.4-2.4-.4s-1.3.4-2.4.4c-1.9 0-3.6-1.2-3.6-3.4 0-2.8 2.4-5.1 5.6-5.1Z" /></symbol>
      <symbol id="i-home" viewBox="0 0 24 24"><path d="M4 10.7 12 4l8 6.7V19a1 1 0 0 1-1 1h-4.4v-5.6H9.4V20H5a1 1 0 0 1-1-1z" /></symbol>
      <symbol id="i-pet" viewBox="0 0 24 24"><path d="M5.2 10V4.8l4 3h5.6l4-3V10a7 7 0 1 1-13.6 0Z" /><path d="M9.4 11.6h.01M14.6 11.6h.01M10.6 14.6c.8.7 2 .7 2.8 0" /></symbol>
      <symbol id="i-chat" viewBox="0 0 24 24"><path d="M3.2 7.4a3.2 3.2 0 0 1 3.2-3.2h6a3.2 3.2 0 0 1 3.2 3.2v3.2A3.2 3.2 0 0 1 12.4 14H8.4l-3.8 3v-2.6a3.2 3.2 0 0 1-1.4-2.6z" /><path d="M18 9.6h.4a2.6 2.6 0 0 1 2.6 2.6v2.4a2.6 2.6 0 0 1-1.7 2.4v2.4l-3.2-2.2h-3.2a2.6 2.6 0 0 1-2.4-1.6" /></symbol>
      <symbol id="i-device" viewBox="0 0 24 24"><path d="M4 7.5h8.5M17 7.5h3M4 16.5h4M12.5 16.5H20" /><circle cx="15" cy="7.5" r="2.2" /><circle cx="10" cy="16.5" r="2.2" /></symbol>
      <symbol id="i-memory" viewBox="0 0 24 24"><path d="M12 3.4 13.9 8.6 19.2 10.5 13.9 12.4 12 17.6 10.1 12.4 4.8 10.5 10.1 8.6Z" /><path d="M18.6 15.4l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" /></symbol>
      <symbol id="i-plugin" viewBox="0 0 24 24"><rect x="4" y="4" width="7" height="7" rx="2" /><rect x="13" y="4" width="7" height="7" rx="2" /><rect x="4" y="13" width="7" height="7" rx="2" /><path d="M16.5 13v3.2M16.5 20.2v.01M13.2 16.7h3.3M20 16.7h-.4" /></symbol>
      <symbol id="i-settings" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1 1.7 1.7V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1Z" /></symbol>
      <symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.2 4.2" /></symbol>
      <symbol id="i-bell" viewBox="0 0 24 24"><path d="M18 9.4a6 6 0 1 0-12 0c0 4.6-1.9 5.6-1.9 5.6h15.8S18 14 18 9.4" /><path d="M10.4 19.4a1.9 1.9 0 0 0 3.2 0" /></symbol>
      <symbol id="i-chevD" viewBox="0 0 24 24"><path d="m6 9.5 6 6 6-6" /></symbol>
      <symbol id="i-chevR" viewBox="0 0 24 24"><path d="m9 5.5 6.5 6.5L9 18.5" /></symbol>
      <symbol id="i-heart" viewBox="0 0 24 24"><path d="M12 20.3S4.6 16 4.6 10.4A4.4 4.4 0 0 1 12 7.1a4.4 4.4 0 0 1 7.4 3.3c0 5.6-7.4 9.9-7.4 9.9Z" /></symbol>
      <symbol id="i-spark" viewBox="0 0 24 24"><path d="M12 3.2 13.7 8.4 18.9 10.1 13.7 11.8 12 17 10.3 11.8 5.1 10.1 10.3 8.4Z" /><path d="M18.8 14.9l.8 2.1 2.1.8-2.1.8-.8 2.1-.8-2.1-2.1-.8 2.1-.8z" /></symbol>
      <symbol id="i-chart" viewBox="0 0 24 24"><path d="M5 20v-9M12 20V4M19 20v-6" /><path d="M3 20h18" /></symbol>
      <symbol id="i-link" viewBox="0 0 24 24"><path d="M10.3 14a4.6 4.6 0 0 0 6.5 0l2-2a4.6 4.6 0 0 0-6.5-6.5l-1 1" /><path d="M13.7 10a4.6 4.6 0 0 0-6.5 0l-2 2a4.6 4.6 0 0 0 6.5 6.5l1-1" /></symbol>
      <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13.2 2.8 5.6 13.6h4.7L9.3 21.2l7.7-11h-4.8z" /></symbol>
      <symbol id="i-camera" viewBox="0 0 24 24"><path d="M4.2 7.6h2.9L8.7 5.2h6.6l1.6 2.4h2.9a1.4 1.4 0 0 1 1.4 1.4v8.6a1.4 1.4 0 0 1-1.4 1.4H4.2a1.4 1.4 0 0 1-1.4-1.4V9a1.4 1.4 0 0 1 1.4-1.4Z" /><circle cx="12" cy="13" r="3.3" /></symbol>
      <symbol id="i-mic" viewBox="0 0 24 24"><rect x="9" y="2.8" width="6" height="11" rx="3" /><path d="M5.4 11.2a6.6 6.6 0 0 0 13.2 0M12 17.8v3M9.2 20.8h5.6" /></symbol>
      <symbol id="i-sensor" viewBox="0 0 24 24"><path d="M3 12h3.6l2-5.6 3.2 11.2 2.6-8.4 1.6 2.8H21" /></symbol>
      <symbol id="i-servo" viewBox="0 0 24 24"><rect x="3.6" y="6" width="16.8" height="12" rx="3.2" /><circle cx="12" cy="12" r="3" /><path d="M12 6v3M12 15v3" /></symbol>
      <symbol id="i-hand" viewBox="0 0 24 24"><path d="M8.2 13.2V6.6a1.6 1.6 0 0 1 3.2 0V12m0-5.4a1.6 1.6 0 0 1 3.2 0V12m0-5a1.6 1.6 0 0 1 3.2 0v6m0-3.2a1.6 1.6 0 0 1 3.2 0v6.2a6 6 0 0 1-6 6h-1.6a5 5 0 0 1-4-2l-3.2-4.3a1.7 1.7 0 0 1 2.6-2.1l1.4 1.4" /></symbol>
      <symbol id="i-game" viewBox="0 0 24 24"><path d="M7.2 8h9.6a4.2 4.2 0 0 1 4.1 5.1l-.8 3.6a2.7 2.7 0 0 1-4.7 1.3L14 16.4h-4l-1.4 1.6a2.7 2.7 0 0 1-4.7-1.3l-.8-3.6A4.2 4.2 0 0 1 7.2 8Z" /><path d="M8 11v3M6.5 12.5h3" /><circle cx="16.2" cy="11.8" r=".9" /><circle cx="18" cy="13.8" r=".9" /></symbol>
      <symbol id="i-music" viewBox="0 0 24 24"><path d="M9 18V5.6L20 3.4V16" /><circle cx="6.4" cy="18" r="2.6" /><circle cx="17.4" cy="16" r="2.6" /></symbol>
      <symbol id="i-smile" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.4" /><path d="M8.6 14a4.4 4.4 0 0 0 6.8 0" /><path d="M9.4 9.6h.01M14.6 9.6h.01" /></symbol>
      <symbol id="i-health" viewBox="0 0 24 24"><path d="M12 3.4 19 6v5.6c0 4.4-2.9 7.2-7 8.8-4.1-1.6-7-4.4-7-8.8V6z" /><path d="M12 15.4s-2.8-1.7-2.8-3.6a1.7 1.7 0 0 1 2.8-1.2 1.7 1.7 0 0 1 2.8 1.2c0 1.9-2.8 3.6-2.8 3.6Z" /></symbol>
      <symbol id="i-battery" viewBox="0 0 24 24"><rect x="2.8" y="8" width="16" height="8" rx="2.4" /><path d="M21.4 11v2" /><path d="M6 11.4h1.4v1.2H6zM9.4 11.4h1.4v1.2H9.4zM12.8 11.4h1.4v1.2h-1.4z" /></symbol>
      <symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12.4 4.4 4.4L19 7.2" /></symbol>
      <symbol id="i-play" viewBox="0 0 24 24"><path d="M8 5.4v13.2L19 12z" /></symbol>
      <symbol id="i-pause" viewBox="0 0 24 24"><rect x="7" y="5.5" width="3.4" height="13" rx="1.2" /><rect x="13.6" y="5.5" width="3.4" height="13" rx="1.2" /></symbol>
      <symbol id="i-close" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18" /></symbol>
      <symbol id="i-menu" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16" /></symbol>
      <symbol id="i-mute" viewBox="0 0 24 24"><path d="M4 9.6h3.4L12 6v12l-4.6-3.6H4z" /><path d="m16.4 9.6 4.4 4.8M20.8 9.6l-4.4 4.8" /></symbol>
      <symbol id="i-shot" viewBox="0 0 24 24"><rect x="3.4" y="6.4" width="17.2" height="12" rx="2.6" /><circle cx="12" cy="12.4" r="3.2" /><path d="M8.6 6.4 9.8 4.4h4.4l1.2 2" /></symbol>
      <symbol id="i-record" viewBox="0 0 24 24"><circle cx="12" cy="12" r="7.6" /><circle cx="12" cy="12" r="3.2" /></symbol>
      <symbol id="i-screen" viewBox="0 0 24 24"><rect x="2.8" y="4.2" width="18.4" height="13.2" rx="2.4" /><path d="M8.4 20.4h7.2M12 17.4v3M9 9.6h.01M15 9.6h.01M9.4 12.2a3.6 3.6 0 0 0 5.2 0" /></symbol>
      <symbol id="i-speaker" viewBox="0 0 24 24"><path d="M4 9.6h3.4L12 5.8v12.4l-4.6-3.8H4z" /><path d="M15.4 9.4a3.6 3.6 0 0 1 0 5.2M18 6.8a7 7 0 0 1 0 10.4" /></symbol>
      <symbol id="i-volume" viewBox="0 0 24 24"><path d="M4 9.6h3.4L12 5.8v12.4l-4.6-3.8H4z" /><path d="M15.5 9h5.5M15.5 15h5.5" /><circle cx="17" cy="9" r="1.4" /><circle cx="19.5" cy="15" r="1.4" /></symbol>
      <symbol id="i-clock" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.4" /><path d="M12 7.2V12l3.4 2" /></symbol>
      <symbol id="i-weather" viewBox="0 0 24 24"><circle cx="8.4" cy="8" r="3.2" /><path d="M8.4 2.6v1.4M8.4 12v1.4M3 8h1.4M12.4 8h1.4M4.6 4.2l1 1M12.2 4.2l-1 1" /><path d="M9 19.4a3.6 3.6 0 0 1 .3-7.2 4.8 4.8 0 0 1 9.2 1.2 3 3 0 0 1-.7 6z" /></symbol>
      <symbol id="i-robot" viewBox="0 0 24 24"><rect x="4.2" y="8" width="15.6" height="11" rx="3.4" /><path d="M12 4.6V8M9.2 19.4v-1M14.8 19.4v-1" /><circle cx="12" cy="3.4" r="1.2" /><path d="M9 13h.01M15 13h.01M9.8 15.8a3 3 0 0 0 4.4 0" /></symbol>
      <symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="3.6" /><path d="M4.6 20a7.4 7.4 0 0 1 14.8 0" /></symbol>
      <symbol id="i-wifi" viewBox="0 0 24 24"><path d="M2.6 8.6a14 14 0 0 1 18.8 0M6 12.3a9 9 0 0 1 12 0M9.3 16a4.2 4.2 0 0 1 5.4 0" /><circle cx="12" cy="19.4" r="1" /></symbol>
      <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14" /></symbol>
      <symbol id="i-power" viewBox="0 0 24 24"><path d="M12 3v9" /><path d="M6.4 6.6a8 8 0 1 0 11.2 0" /></symbol>
      <symbol id="i-refresh" viewBox="0 0 24 24"><path d="M20 11a8 8 0 1 0-2.2 6" /><path d="M20 5v6h-6" /></symbol>
      <symbol id="i-info" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8.4" /><path d="M12 11v5M12 8h.01" /></symbol>
      <symbol id="i-signal" viewBox="0 0 24 24"><path d="M4 18v-3M9 18v-6M14 18v-9M19 18V6" /></symbol>
      <symbol id="i-location" viewBox="0 0 24 24"><path d="M12 21s6.4-5.4 6.4-10.4A6.4 6.4 0 0 0 5.6 10.6C5.6 15.6 12 21 12 21Z" /><circle cx="12" cy="10.4" r="2.2" /></symbol>
      <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20 14.4A8 8 0 0 1 9.6 4 8.4 8.4 0 1 0 20 14.4Z" /></symbol>
    </defs>
  </svg>
</template>
