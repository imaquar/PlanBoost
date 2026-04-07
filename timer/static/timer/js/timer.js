(function () {
    const WORK_DURATION_SECONDS = 30 * 60;
    const BREAK_DURATION_SECONDS = 5 * 60;
    const displayElement = document.getElementById('timer-display');
    const modeElement = document.getElementById('timer-mode');
    const startButton = document.getElementById('start-button');
    const pauseButton = document.getElementById('pause-button');
    const resetButton = document.getElementById('reset-button');

    if (!displayElement || !modeElement || !startButton || !pauseButton || !resetButton) {
        return;
    }

    let mode = 'work';
    let remainingSeconds = WORK_DURATION_SECONDS;
    let intervalId = null;

    function formatTime(totalSeconds) {
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    function modeLabel(currentMode) {
        return currentMode === 'work' ? 'work' : 'break';
    }

    function render() {
        displayElement.textContent = formatTime(remainingSeconds);
        modeElement.textContent = modeLabel(mode);
    }

    function stopInterval() {
        if (intervalId !== null) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }

    function switchMode() {
        mode = mode === 'work' ? 'break' : 'work';
        remainingSeconds = mode === 'work' ? WORK_DURATION_SECONDS : BREAK_DURATION_SECONDS;
        render();
    }

    function tick() {
        if (remainingSeconds <= 1) {
            switchMode();
            return;
        }

        remainingSeconds -= 1;
        render();
    }

    function startTimer() {
        if (intervalId !== null) {
            return;
        }

        intervalId = setInterval(tick, 1000);
    }

    function pauseTimer() {
        stopInterval();
    }

    function resetTimer() {
        stopInterval();
        mode = 'work';
        remainingSeconds = WORK_DURATION_SECONDS;
        render();
    }

    startButton.addEventListener('click', startTimer);
    pauseButton.addEventListener('click', pauseTimer);
    resetButton.addEventListener('click', resetTimer);

    render();
})();