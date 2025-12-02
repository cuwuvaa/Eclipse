document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('join-by-id-modal');
  const btn = document.getElementById('join-by-id-btn');
  const span = document.getElementsByClassName('close-btn')[0];
  const form = document.getElementById('join-by-id-form');
  const input = document.getElementById('room-id-input');

  btn.onclick = () => {
    modal.style.display = 'block';
  };

  span.onclick = () => {
    modal.style.display = 'none';
  };

  window.onclick = (event) => {
    if (event.target == modal) {
      modal.style.display = 'none';
    }
  };

  form.onsubmit = (event) => {
    event.preventDefault();
    const roomId = input.value;
    if (roomId) {
      window.location.href = `/${roomId}/`;
    }
  };
});
