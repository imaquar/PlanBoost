(function () {
    let workDurationSeconds = 30 * 60;
    let breakDurationSeconds = 5 * 60;
    const displayElement = document.getElementById('timer-display');
    const modeElement = document.getElementById('timer-mode');
    const startButton = document.getElementById('start-button');
    const pauseButton = document.getElementById('pause-button');
    const resetButton = document.getElementById('reset-button');
    const setButton = document.getElementById('set-button');
    const timerSetForm = document.getElementById('timer-set-form');
    const workInput = document.getElementById('work-input');
    const breakInput = document.getElementById('break-input');
    const cancelSetButton = document.getElementById('cancel-set-button');

    if (!displayElement || !modeElement || !startButton || !pauseButton || !resetButton) {
        return;
    }

    let mode = 'work';
    let remainingSeconds = workDurationSeconds;
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
        remainingSeconds = mode === 'work' ? workDurationSeconds : breakDurationSeconds;
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
        remainingSeconds = workDurationSeconds;
        render();
    }

    function parseMinutesSeconds(value) {
        const text = String(value || '').trim();
        const parts = text.split(':');

        if (parts.length !== 2) {
            return null;
        }

        const minutes = Number(parts[0]);
        const seconds = Number(parts[1]);

        if (!Number.isInteger(minutes) || !Number.isInteger(seconds)) {
            return null;
        }

        if (minutes < 0 || seconds < 0 || seconds > 59) {
            return null;
        }

        const total = minutes * 60 + seconds;
        return total > 0 ? total : null;
    }

    function toggleSetForm() {
        if (!timerSetForm) {
            return;
        }
        timerSetForm.hidden = !timerSetForm.hidden;
    }

    function hideSetForm() {
        if (!timerSetForm) {
            return;
        }
        timerSetForm.hidden = true;
    }

    startButton.addEventListener('click', startTimer);
    pauseButton.addEventListener('click', pauseTimer);
    resetButton.addEventListener('click', resetTimer);

    if (setButton) {
        setButton.addEventListener('click', toggleSetForm);
    }

    if (cancelSetButton) {
        cancelSetButton.addEventListener('click', hideSetForm);
    }

    if (timerSetForm) {
        timerSetForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const nextWork = parseMinutesSeconds(workInput ? workInput.value : '');
            const nextBreak = parseMinutesSeconds(breakInput ? breakInput.value : '');

            if (!nextWork || !nextBreak) {
                window.alert('Use m:s format, example: 30:00 and 5:00');
                return;
            }

            workDurationSeconds = nextWork;
            breakDurationSeconds = nextBreak;
            hideSetForm();
            resetTimer();
        });
    }

    render();
})();