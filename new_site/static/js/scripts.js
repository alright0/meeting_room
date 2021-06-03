// функция обновления списка встречь
function update_meetings(user_id, csrftoken) {
    $.ajax({
        type: 'post',
        mode: 'same-origin',

        data: { "id": user_id, "csrfmiddlewaretoken": csrftoken },
        success: function (response) {

            $(".meetings").html("")

            document.getElementsByClassName('meetings').innerHTML = ""

            $.each(response, function (record) {
                rec = response[record];

                $(".meetings").append(`
                <div class="meeting" id="meeting_id ${rec.id}">
                <p>${rec.room_id__name}</p>
                <p>Организатор встречи: ${rec.oraganizator_id__first_name} ${rec.oraganizator_id__last_name}</p>
                <input type="submit" value="Принять" onclick="send_meeting_answer('accept', this)">
                <input type="submit" value="Отклонить" onclick="send_meeting_answer('decline', this)">
                </div>
                `)

            });

        },
    },
    )
};
