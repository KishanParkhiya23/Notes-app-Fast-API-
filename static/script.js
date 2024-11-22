$(document).ready(function () {

    $(".fixed").each(function (event) {
        if (event.target === this) {
            $(this).addClass("hidden");
        }
    });

    $('#filter').on("change", function () {
        var filter = $(this).val();
        var filterObject = {};
        if (['ASC', 'DESC'].includes(filter)) {
            filterObject['sort'] = filter;
        } else if (['IMP', 'NOT_IMP'].includes(filter)) {
            filterObject['important'] = filter == "IMP" ? true : false;
        }

        const url = filterObject && Object.keys(filterObject).length ? `/get_all_notes/?filter=${encodeURIComponent(JSON.stringify(filterObject))}` : `/get_all_notes/`;

        $.ajax({
            url: url,
            method: "GET",
            dataType: "json",
            success: function (response) {
                const notesContainer = $("#notes-container");
                notesContainer.empty();

                if (response.length === 0) {
                    notesContainer.html("<span>No matching records found</span>");
                } else {
                    notesContainer.append(createNotesHTML(response));
                }
            },
            error: function (xhr, status, error) {
                console.error("Error fetching notes:", error);
                const notesContainer = $("#notes-container");
                notesContainer.html("<span>Error fetching notes. Please try again later.</span>");
            }
        });
    });

});
function toggleReadMore(id) {
    $(`#${id}`).toggleClass("hidden");
}

function openModal(id) {
    $(`#${id}`).removeClass("hidden");
}

function closeModal(id) {
    $(`#${id}`).addClass("hidden");
}

function createNotesHTML(notes) {
    const fragment = $(document.createDocumentFragment());
    notes.forEach((note, index) => {
        const noteElement = $(`
            <div class="relative bg-white shadow-lg rounded-lg p-6 border-t-4 ${note.is_important ? "border-red-500" : "border-indigo-500"}">
                <h6 class="text-lg font-bold text-gray-800">${note.title}</h6>
                <div class="mt-2">
                    <button class="text-sm text-indigo-600 hover:underline" onclick="toggleReadMore('collapse${index}')">
                        Read note
                    </button>
                    <button class="text-sm text-red-600 hover:underline float-right" onclick="toggleDeleteModal(true, '${note.id}')">
                        Delete
                    </button>
                    <button class="text-sm text-indigo-600 hover:underline float-right mr-2" onclick="openModal('modal${index}')">
                        Edit
                    </button>
                </div>
                <div id="collapse${index}" class="hidden mt-4 text-sm text-gray-600">
                    ${note.content}
                </div>
                <div id="modal${index}" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div class="bg-white p-6 rounded-lg shadow-lg w-100">
                        <h5 class="text-lg font-semibold text-gray-700">Edit Note</h5>
                        <form action="/update/${note.id}" method="post" class="mt-4">
                            <label class="inline-flex items-center mb-2 float-end">
                                <input type="checkbox" name="is_important" ${note.is_important ? "checked" : ""} class="form-checkbox text-indigo-600" />
                                <span class="ml-2 text-sm text-gray-600">Important</span>
                            </label>
                            <input type="text" name="title" value="${note.title}" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring focus:ring-indigo-300 focus:outline-none" />
                            <textarea name="content" class="w-full px-4 py-2 mt-4 border border-gray-300 rounded-lg focus:ring focus:ring-indigo-300 focus:outline-none">${note.content}</textarea>
                            <div class="flex justify-end space-x-2 mt-4">
                                <button type="button" class="btn btn-light btn-sm mt-3 pt-1 pb-2 px-3 text-sm rounded-md bg-gray-300 text-gray-800 hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500" onclick="closeModal('modal${index}')">
                                    Cancel
                                </button>
                                <button type="submit" class="btn btn-dark btn-sm mt-3 pt-1 pb-2 px-3 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                                    Update
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `);

        fragment.append(noteElement);
    });

    return fragment;
}

async function fetchNotesByTitle() {
    try {
        const data = $('#search-input').val();
        const url = data ? `/find_notes/${encodeURIComponent(data)}` : `/get_all_notes/`;
        const response = await $.ajax({
            url: url,
            method: "GET",
            dataType: "json",
        });
        console.log("response", response);

        const notesContainer = $("#notes-container");
        notesContainer.empty();

        if (response.length === 0) {
            notesContainer.html("<span>No matching records found</span>");
        } else {
            notesContainer.append(createNotesHTML(response));
        }
    } catch (error) {
        console.error("Error fetching notes:", error);
    }
}

function toggleDeleteModal(show, noteId) {
    const modal = $("#deleteModal");
    const deleteBtn = $("#deleteBtn");

    deleteBtn.off("click").on("click", function () {
        window.location.href = `/delete/${noteId}`;
    });

    if (show) {
        modal.removeClass("hidden");
    } else {
        modal.addClass("hidden");
    }
}
