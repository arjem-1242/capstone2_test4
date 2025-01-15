//
// // Function to update the field when the input changes
// function updateField(input) {
//     const field = input.dataset.field;
//     const id = input.dataset.id;
//     let value = input.value; // Get the value of the selected date (yyyy-mm-dd or dd/mm/yyyy)
//
//     // Convert the date format if necessary
//     if (value.includes("/")) {
//         value = convertDateFormat(value);
//     }
//
//     // Send the formatted date to the server
//     fetch("jobseeker/jobseeker/update_profile/", {
//         method: "POST",
//         headers: {
//             "Content-Type": "application/json",
//             "X-CSRFToken": getCSRFToken(),
//         },
//         body: JSON.stringify({ id, field, value }),
//     })
//         .then((response) => response.json())
//         .then((data) => {
//             if (data.success) {
//                 console.log("Field updated successfully!");
//             } else {
//                 alert("Failed to update field.");
//             }
//         })
//         .catch((error) => console.error("Error updating field:", error));
// }
//
//
//
//
// let originalData = {};
//
// $(document).ready(function () {
//     console.log(updateProfileBulkUrl);
//
//     // Store original data on load
//     $(".editable").each(function () {
//         const field = $(this).data("field");
//         const id = $(this).data("id") || "global";
//         if (!originalData[id]) {
//             originalData[id] = {};
//         }
//         originalData[id][field] = $(this).text().trim();
//     });
//
//     // Save changes
//     $("#save-changes").on("click", function () {
//         const changes = [];
//         $(".editable").each(function () {
//             const content = $(this).text().trim();
//             const field = $(this).data("field");
//             const id = $(this).data("id");
//
//             changes.push({ id: id || null, field: field, value: content });
//         });
//
//         // Send AJAX request to save changes
//         $.ajax({
//             type: "POST",
//             url: updateProfileBulkUrl, // Use the dynamically injected URL
//             data: {
//                 csrfmiddlewaretoken: getCSRFToken(),
//                 changes: JSON.stringify(changes),
//             },
//             success: function (response) {
//                 $("#status-message")
//                     .text("Changes saved successfully!")
//                     .addClass("success")
//                     .removeClass("error");
//             },
//             error: function () {
//                 $("#status-message")
//                     .text("Failed to save changes.")
//                     .addClass("error")
//                     .removeClass("success");
//             },
//         });
//     });
//
//     // Discard changes
//     $("#discard-changes").on("click", function () {
//         $(".editable").each(function () {
//             const field = $(this).data("field");
//             const id = $(this).data("id") || "global";
//             $(this).text(originalData[id][field]);
//         });
//         $("#status-message").text("Changes discarded.").removeClass("success error");
//     });
//
//     // Bind the updateField function to date inputs
//     $(".editable-date").on("change", function () {
//         updateField(this);
//     });
// });
//
// // Function to convert dd/mm/yyyy to yyyy-mm-dd
// function convertDateFormat(date) {
//     if (!date.includes("/")) {
//         return date; // If the date is already in yyyy-mm-dd format, return as-is
//     }
//     const [day, month, year] = date.split("/");
//     return `${year}-${month}-${day}`; // Convert dd/mm/yyyy to yyyy-mm-dd
// }
//
// // Function to get the CSRF token from the HTML
// function getCSRFToken() {
//     const tokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
//     return tokenElement ? tokenElement.value : null;
// }