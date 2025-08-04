(function() {
    let idleTime = 0;
    let alertShown = false;

    const logoutUrl = window.idleLogoutUrl || "/logout/";

    const idleInterval = setInterval(() => {
        idleTime++;

        if (idleTime === 8 && !alertShown) {
            alert("You've been inactive for a while. You’ll be logged out in 2 minutes if there's no activity.");
            alertShown = true;
        }

        if (idleTime >= 10) {
            clearInterval(idleInterval);
            window.location.href = logoutUrl;
        }
    }, 60000); // 10 minute

    const resetIdleTimer = () => {
        idleTime = 0;
        alertShown = false;
    };

    window.onload = resetIdleTimer;
    document.onmousemove = resetIdleTimer;
    document.onkeypress = resetIdleTimer;
    document.onscroll = resetIdleTimer;
    document.onclick = resetIdleTimer;
})();
