$(document).ready(function () {
    $(".fixed").each(function (event) {
        if (event.target === this) {
            $(this).addClass("hidden");
        }
    });

    $("#closeUpdateModal").on('click', function () {
        $(`#UpdateModal`).addClass("hidden");
    })

    $('#filter').on("change", function () {
        var filter = $(this).val();
        var filterObject = {};
        if (['ASC', 'DESC'].includes(filter)) {
            filterObject['sort'] = filter;
        } else if (['IMP', 'NOT_IMP'].includes(filter)) {
            filterObject['important'] = filter == "IMP" ? true : false;
        } else if (filter == "ALL") {
            filterObject['all'] = true
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

function hideNoteImage() {
    $("#modal-noteImg").css("display", $("#modal-deleteFile").is(":checked") ? "none" : "block");
}

function toggleReadMore(id) {
    $(`#${id}`).toggleClass("hidden");
}

function openUpdateModal(id) {
    $.ajax({
        url: `/find_notes_by_id/${id}`,
        method: "GET",
        dataType: "json",
        success: function (response) {
            if (response) {
                $("#modal-form").attr('action', `/update/${response.id}`)
                $("#modal-is_important").attr('checked', response.is_important)
                $("#modal-title").val(response.title)
                $("#modal-content").text(response.content)
                if (response.noteFile) {
                    let content = ``
                    content += `<input type="checkbox" name="deleteFile" id="modal-deleteFile" value="DELETE" class="mr-2 mb-2" onchange="hideNoteImage()">`
                    content += `<label for="modal-deleteFile">Remove</label>`
                    content += `<img src="${response.noteFile}" id="modal-noteImg" alt="Note file" width="100px" class="h-auto max-w-full rounded-lg"></img>`
                    $("#modal-image-section").empty().append(content)
                }
                $(`#UpdateModal`).removeClass("hidden");
            } else {
                console.error("No data received.");
            }
        },
        error: function (xhr, status, error) {
            alert("An error occurred: " + xhr.responseText);
        },
    });

}

function createNotesHTML(notes) {
    const fragment = $(document.createDocumentFragment());
    notes.forEach((note, index) => {
        const noteElement = $(`
            <div class="relative bg-white shadow-lg rounded-lg px-6 pb-6 pt-4 border-t-4 ${note.is_important ? "border-red-500" : "border-indigo-500"}">
                <div class="flex justify-end">
                    <button class="text-sm text-indigo-600 hover:underline mr-3" onclick="openUpdateModal('${note.id}')">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button class="text-sm text-red-600 hover:underline" onclick="toggleDeleteModal(true, '${note.id}')">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
                <h6 class="text-lg font-bold text-gray-800">${note.title}</h6>
                <div class="mt-2">
                    <button class="text-sm text-indigo-600 hover:underline" onclick="toggleReadMore('collapse${index}')">
                        Read note
                    </button>
                </div>
                <div id="collapse${index}" class="hidden mt-4 text-sm text-gray-600">
                    ${note.content}
                    ${note.noteFile}
                    ${note.noteFile ? `<img src="${note.noteFile}" alt="Note file" width="50px" class="h-auto max-w-full rounded-lg">` : ""}
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
        window.location.href = `/ delete/${noteId}`;
    });

    if (show) {
        modal.removeClass("hidden");
    } else {
        modal.addClass("hidden");
    }
}