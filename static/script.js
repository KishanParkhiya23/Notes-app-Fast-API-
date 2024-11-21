
// Toggle Read More Section
function toggleReadMore(id) {
    const element = document.getElementById(id);
    element.classList.toggle("hidden");
}

// Open Modal
function openModal(id) {
    const modal = document.getElementById(id);
    modal.classList.remove("hidden");
}

// Close Modal
function closeModal(id) {
    const modal = document.getElementById(id);
    modal.classList.add("hidden");
}

// Close Modal on clicking the background
window.onclick = function (event) {
    const modals = document.querySelectorAll(".fixed");
    modals.forEach((modal) => {
        if (event.target === modal) {
            modal.classList.add("hidden");
        }
    });
};

function createNoteHTML(note, index) {
    const noteElement = document.createElement("div");
    noteElement.classList.add("relative", "bg-white", "shadow-lg", "rounded-lg", "p-6", "border-t-4");

    noteElement.classList.add(note.is_important ? "border-red-500" : "border-indigo-500");

    noteElement.innerHTML = `
        <h6 class="text-lg font-bold text-gray-800">${note.title}</h6>
        <div class="mt-2">
            <button class="text-sm text-indigo-600 hover:underline" onclick="toggleReadMore('collapse${index}')">
                Read note
            </button>
            <button class="text-sm text-indigo-600 hover:underline float-right" onclick="openModal('modal${index}')">
                Edit
            </button>
        </div>
        <div id="collapse${index}" class="hidden mt-4 text-sm text-gray-600">
            ${note.content}
        </div>
        <div id="modal${index}"
            class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white p-6 rounded-lg shadow-lg w-100">
                <h5 class="text-lg font-semibold text-gray-700">Edit Note</h5>
                <form action="/update/${note.id}" method="post" class="mt-4">
                    <label class="inline-flex items-center mb-2 float-end">
                        <input type="checkbox" name="is_important" {% if doc.is_important %}checked{% endif
                            %} class="form-checkbox text-indigo-600" />
                        <span class="ml-2 text-sm text-gray-600">Important</span>
                    </label>
                    <input type="text" name="title" value="${note.title}"
                        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring focus:ring-indigo-300 focus:outline-none" />
                    <textarea name="content"
                        class="w-full px-4 py-2 mt-4 border border-gray-300 rounded-lg focus:ring focus:ring-indigo-300 focus:outline-none">${note.content}</textarea>
                    <div class="flex justify-end space-x-2 mt-4">
                        <button type="button"
                            class="btn btn-light btn-sm mt-3 pt-1 pb-2 px-3 text-sm rounded-md bg-gray-300 text-gray-800 hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                            onclick="closeModal('modal${index}')">
                            Cancel
                        </button>
                        <button type="submit"
                            class="btn btn-dark btn-sm mt-3 pt-1 pb-2 px-3 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            Update
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;

    return noteElement;
}


async function fetchNotesByTitle() {
    try {
        const data = document.getElementById('search-input');

        // URL of the FastAPI endpoint
        const url = data.value ? `/find_notes/${encodeURIComponent(data.value)}` : `/get_all_notes/`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Error: ${response.status} - ${response.statusText}`);
        }
        const notes = await response.json();
        console.log(notes.length);
        const notesContainer = document.getElementById("notes-container");
        notesContainer.innerHTML = "";
        if (notes.length == 0) {
            notesContainer.innerHTML = "<span>No matching records found</span>";

        } else {
            notes.forEach((note, index) => {
                const noteElement = createNoteHTML(note, index);
                notesContainer.appendChild(noteElement);
            });
        }

    } catch (error) {
        console.error("Error fetching notes:", error);
    }
}
// fetchNotesByTitle("note")

