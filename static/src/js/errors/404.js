export default function init404Error() {
    const svgEl = document.getElementById('road-svg');
    const bus = document.getElementById('bus');
    const question = document.getElementById('question');
    const questionText = document.getElementById('question-text');
    const spoke1a = document.getElementById('spoke1a');
    const spoke1b = document.getElementById('spoke1b');
    const spoke2a = document.getElementById('spoke2a');
    const spoke2b = document.getElementById('spoke2b');

    if (!svgEl || !bus) return;

    const viewWidth = svgEl.viewBox.baseVal.width;

    if (questionText) {
        questionText.setAttribute('x', (viewWidth / 2) - 10);
    }

    let x = -180;
    let angle = 0;
    let phase = 'enter';
    let pauseTimer = 0;
    let questionOpacity = 0;
    let frame = 0;
    let bounceY = 0;

    const stopPosition = (viewWidth / 2) - 80;

    function animate() {
        frame++;

        if (phase === 'enter') {
            x += 3.5;
            angle += 5;
            bounceY = Math.sin(frame * 0.22) * 1.2;

            if (x >= stopPosition) {
                x = stopPosition;
                phase = 'pause';
                pauseTimer = 0;
            }
        } else if (phase === 'pause') {
            pauseTimer++;
            bounceY = 0;
            questionOpacity = Math.min(1, questionOpacity + 0.04);
            if (question) question.setAttribute('opacity', questionOpacity);
            if (pauseTimer > 90) { phase = 'exit'; }
        } else if (phase === 'exit') {
            x += 4.5;
            angle += 6;
            bounceY = Math.sin(frame * 0.22) * 1.2;
            questionOpacity = Math.max(0, questionOpacity - 0.05);
            if (question) question.setAttribute('opacity', questionOpacity);

            if (x > viewWidth) {
                x = -180;
                phase = 'enter';
                questionOpacity = 0;
                if (question) question.setAttribute('opacity', 0);
            }
        }

        bus.setAttribute('transform', `translate(${x}, ${bounceY})`);

        const cx1 = 30, cy1 = 153, cx2 = 128, cy2 = 153;
        const rad = angle * Math.PI / 180;

        if (spoke1a) {
            spoke1a.setAttribute('x1', cx1 + 13 * Math.cos(rad - Math.PI / 2));
            spoke1a.setAttribute('y1', cy1 + 13 * Math.sin(rad - Math.PI / 2));
            spoke1a.setAttribute('x2', cx1 - 13 * Math.cos(rad - Math.PI / 2));
            spoke1a.setAttribute('y2', cy1 - 13 * Math.sin(rad - Math.PI / 2));
        }
        if (spoke1b) {
            spoke1b.setAttribute('x1', cx1 + 13 * Math.cos(rad));
            spoke1b.setAttribute('y1', cy1 + 13 * Math.sin(rad));
            spoke1b.setAttribute('x2', cx1 - 13 * Math.cos(rad));
            spoke1b.setAttribute('y2', cy1 - 13 * Math.sin(rad));
        }

        if (spoke2a) {
            spoke2a.setAttribute('x2', cx2 - 13 * Math.cos(rad - Math.PI / 2));
            spoke2a.setAttribute('y1', cy2 + 13 * Math.sin(rad - Math.PI / 2));
            spoke2a.setAttribute('x1', cx2 + 13 * Math.cos(rad - Math.PI / 2));
            spoke2a.setAttribute('y2', cy2 - 13 * Math.sin(rad - Math.PI / 2));
        }
        if (spoke2b) {
            spoke2b.setAttribute('x1', cx2 + 13 * Math.cos(rad));
            spoke2b.setAttribute('y1', cy2 + 13 * Math.sin(rad));
            spoke2b.setAttribute('x2', cx2 - 13 * Math.cos(rad));
            spoke2b.setAttribute('y2', cy2 - 13 * Math.sin(rad));
        }

        requestAnimationFrame(animate);
    }

    animate();
}
