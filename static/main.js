// ─── Delete Confirmation ───
function confirmDelete() {
    return confirm("Are you sure you want to delete this task?");
}

// ─── Enable Edit Mode ───
function enableEdit(button) {
    const taskCard = button.closest(".task-card");
    const taskInfo = taskCard.querySelector(".task-info");
    const editForm = taskCard.querySelector(".edit-form");
    const taskActions = taskCard.querySelector(".task-actions");

    taskInfo.classList.add("hidden");
    taskActions.classList.add("hidden");
    editForm.classList.remove("hidden");
    editForm.querySelector("input").focus();
}

// ─── Cancel Edit Mode ───
function cancelEdit(button) {
    const taskCard = button.closest(".task-card");
    const taskInfo = taskCard.querySelector(".task-info");
    const editForm = taskCard.querySelector(".edit-form");
    const taskActions = taskCard.querySelector(".task-actions");

    editForm.classList.add("hidden");
    taskInfo.classList.remove("hidden");
    taskActions.classList.remove("hidden");
}