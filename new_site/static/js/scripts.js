// функция обновления списка встречь
function update_meetings(user_id, csrftoken) {
    $.ajax({
        type: 'post',
        mode: 'same-origin',

        data: { "id": user_id, "csrfmiddlewaretoken": csrftoken },
        success: function (response) {
            $(".meetings").html("")
            document.getElementsByClassName('meetings').innerHTML = ""

            //Для каждой встречи создать контейнер
            $.each(response, function (record) {
                rec = response[record];
                start_time = format_date(new Date(rec.start_time))
                end_time = format_date(new Date(rec.end_time))

                $(".meetings").append(`
                <div class="meeting" id="meeting_id ${rec.id}">
                <p>Организатор встречи: ${rec.organizator_id__first_name} ${rec.organizator_id__last_name}</p>
                <p>Время встречи с: ${start_time} до: ${end_time}</>
                <p>Место: ${rec.room_id__name}. Тема: ${rec.title}</p>
                <input type="submit" value="Принять" onclick="send_meeting_answer('accept', this)">
                <input type="submit" value="Отклонить" onclick="send_meeting_answer('decline', this)">
                </div>
                `)

            });

        },
    },
    )
};

/** функция добавления нулей к строкам. Принимает строку и количество символов 
 * для заполнения слева. Пример: zfill("5", 2) -> '05', zfill("2525", 2) -> '2525'*/
function zfill(num, length) {
    return String(num).padStart(length, "0");
};

// функция приведения даты к виду "02.05.2021 15:30"
function format_date(s_) {
    return `${zfill(s_.getDate(), 2)}.${zfill(s_.getMonth(), 2)}.${s_.getFullYear()} \
    ${zfill(s_.getHours(), 2)}:${zfill(s_.getMinutes(), 2)}`
};