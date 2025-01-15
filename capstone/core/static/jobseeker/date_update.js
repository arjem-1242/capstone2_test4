//
//
// function updateField(input) {
//     const field = input.dataset.field;
//     const id = input.dataset.id;
//     const value = input.value;
//
//     fetch('jobseeker/update_profile/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//             'X-CSRFToken': getCSRFToken(),
//         },
//         body: JSON.stringify({ id, field, value }),
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             console.log('Field updated successfully!');
//         } else {
//             alert('Failed to update field.');
//         }
//     })
//     .catch(error => console.error('Error updating field:', error));
// }
//
// function getCSRFToken() {
//     return document.querySelector('[name=csrfmiddlewaretoken]').value;
// }