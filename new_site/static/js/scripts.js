// функция обновления списка встречь
function update_meetings(user_id, csrftoken) {
    $.ajax({
        type: 'post',
        mode: 'same-origin',
        data: { "id": user_id, "csrfmiddlewaretoken": csrftoken },
        success: function (response) {
            $(".meetings").html("")
            $(".meetings").append("<h2>Встречи для согласования</h2>")

            if (!response.length) {
                $(".meetings").append('<p style="text-align:center;">Новых встречь нет.</p>')
            }

            //Для каждой встречи создать контейнер
            $.each(response, function (record) {
                rec = response[record];
                start_time = format_date(new Date(rec.start_time))
                end_time = format_date(new Date(rec.end_time))

                $(".meetings").append(`
                <div class="meeting" id="meeting_id_${rec.id}">
                <p><b>Организатор встречи:</b> ${rec.organizator_id__first_name} ${rec.organizator_id__last_name}</p>
                <p><b>Дата:</b> ${start_time.slice(0, 8)} <b>Время встречи с:</b> ${start_time.slice(-5)} <b>до</b>: ${end_time.slice(-5)}</>
                <p><b>Место:</b> ${rec.room_id__name}. <b>Тема:</b> ${rec.title}</p>
                <input type="submit" value="Принять" class="accept" onclick="send_meeting_answer('accept', String(this.parentNode.id))">
                <input type="submit" value="Отклонить" class="decline" onclick="send_meeting_answer('decline', String(this.parentNode.id))">
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
    return `${zfill(s_.getDate(), 2)}.${zfill(s_.getMonth(), 2)}.${s_.getFullYear()} ${zfill(s_.getHours(), 2)}:${zfill(s_.getMinutes(), 2)}`
};

// функция вызывается при подтверждении/отклоненнии встречи менеджером. 
function create_html_answer(answer, container_id) {

    if (answer == "accept") {
        answer_local = "подтвердили"
        bgcolor = "rgb(224, 247, 212)"
    } else {
        answer_local = "отклонили"
        bgcolor = "rgb(247, 212, 212)"
    }

    $(`#${container_id}`).html(`
                <p style="background-color: ${bgcolor};">Вы ${answer_local} встречу!</p>
                `)

}

// формирует сообщение для уведомлений
function create_notification(e) {
    const data = JSON.parse(e.data)

    if (data.answer == "accept") {
        var answer = "подтвердил(а)"
    } else {
        var answer = "отклонил(а)"
    }

    title_str = `Собрание в ${format_date(new Date(data.start_time))}\nТема: ${data.title}`
    body_str = `${data.manager_id__first_name} ${data.manager_id__last_name} ${answer} встречу`

    return { "title": title_str, 'body': body_str }
}