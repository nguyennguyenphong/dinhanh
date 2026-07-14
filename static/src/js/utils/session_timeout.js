(function () {
    const INACTIVITY_TIMEOUT = 15 * 60 * 1000;
    let timeoutId;
    const redirectUrl = document.body.dataset.timeoutUrl;

    if (!redirectUrl) return;

    function resetTimer() {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(logoutOrRedirect, INACTIVITY_TIMEOUT);
    }

    function logoutOrRedirect() {
        window.location.href = redirectUrl;
    }

    window.onload = resetTimer;
    document.onmousemove = resetTimer;
    document.onkeydown = resetTimer;
    document.onscroll = resetTimer;
    document.onclick = resetTimer;
})();
