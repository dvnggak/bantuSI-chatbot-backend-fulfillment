from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper

import uuid

app = FastAPI()

def generate_session_id():
    return str(uuid.uuid4())


@app.post("/")
async def handle(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the Webhook Request from dialogflow
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]

    # Get or generate the session ID
    session_id = get_or_generate_session_id(output_contexts)


    # Perform the necessary logic based on the intent
    if intent == "validate.user" :
        return validate_user(parameters, session_id)
    elif intent == "informations.select" :
        return informations_select(parameters, output_contexts)
    elif intent == "track-subject" :
        return track_subject(parameters)  
    elif intent == "track-announcement-categories" :
        return track_announcements(parameters)

def get_or_generate_session_id(output_contexts: list):
    # Try to find the session ID in the output contexts
    for context in output_contexts:
        if context["name"].endswith("/contexts/session"):
            return context["parameters"]["sessionId"]

    # If not found, generate a new session ID
    new_session_id = generate_session_id()
    return new_session_id
    
def validate_user(parameters: dict, session_id: str ):

    nim = parameters["number"]
    name = db_helper.check_user_exists(nim)

    if name:
        fulfillment_text = (
            f"Halo kak {name} \U0001F44B,\n\n"  # Unicode for waving hand emoji
    "Saya dapat memberikan informasi tentang beberapa hal yang ada di Prodi Sistem Informasi, diantaranya:\n\n"
    "    1. Profil Prodi \n"
    "       - Deskripsi Profil \n"
    "       - Struktur Organisasi\n"
    "       - Daftar Dosen\n\n"
    "    2. Perkuliahan\n"
    "       - Syarat Skripsi\n"
    "       - Panduan Skripsi\n"
    "       - Syarat Kerja Praktek\n"
    "       - Panduan Kerja Praktek\n"
    "       - Mata Kuliah\n\n"
    "    3. Pembayaran\n"
    "       - Panduan Pembayaran\n"
    "       - Jadwal Pembayaran\n\n"
    "    4. Pengumuman\n\n"
    "    5. Berkas Akademik\n\n"
    "Kamu bisa membalas pesan ini dengan menuliskan daftar informasi di atas seperti \"Berikan informasi mengenai Mata Kuliah \U0001F4DA..."
        )
        # Set the "validated" context if validation is successful
        output_contexts = [
            {
                "name": f"projects/bantusi-ukoi/agent/sessions/{session_id}/contexts/validated",
                "lifespanCount": 2,
            }
        ]
    else:
        fulfillment_text = "Maaf, sepertinya NIM kamu salah atau tidak terdaftar... \n\nSilahkan kirimkan ulang NIM kamu atau hubungi bagian administrasi ya :D."
        output_contexts = [
            {
                "name": f"projects/bantusi-ukoi/agent/sessions/{session_id}/contexts/defaultwelcomeintent-followup",
                "lifespanCount": 2,
            }
        ]

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
        "outputContexts": output_contexts,
    })

def informations_select(parameters: dict, output_contexts: list):
    # Check for the "validated" context
    # If it exists, then the user has been validated
    validated_context = next((context for context in output_contexts if context["name"].endswith("/contexts/validated")), None)

    # initialize the fulfillment text variable string

    fulfillment_text = ""
    if validated_context:
        # Extract the "information" parameter
        information_item = parameters["informations_item"]

        # Perform the necessary logic based on the extracted information item
        if information_item == "Mata Kuliah":
            fulfillment_text = (
                f"Baik, Bisakah Kakak menginformasi kan Kode Mata Kuliah nya ?\n\n"
            )
        elif information_item == "Struktur Organisasi":
            # Sent image of the organizational structure on Telegram
            fulfillment_text = (
                f"Baik, Berikut adalah Struktur Organisasi Prodi Sistem Informasi : \n\n"
                f"https://ibb.co/w6M3F4Z \n\n"
                f"Semoga membantu ya kak :D"
            )
        elif information_item == "Daftar Dosen":
            lecturers = db_helper.get_lecturers()
            fulfillment_text = (
                f"Baik, Berikut adalah Daftar Dosen Prodi Sistem Informasi : \n\n"
            )
            for lecturer in lecturers:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n\n"
                    f"NIK/NIDN : {lecturer[1]}/{lecturer[2]} \n"
                    f"Nama : {lecturer[3]} \n"
                    f"Jenis Kelamin : {lecturer[4]} \n\n"
                    f"Universitas : {lecturer[5]} \n"
                    f"Fakultas : {lecturer[6]} \n"
                    f"Prodi : {lecturer[7]} \n\n"
                    f"Jabatan Fungsional : {lecturer[8]} \n"
                    f"Status Ikatan Kerja : {lecturer[9]} \n"
                    f"Pendidikan Tertinggi : {lecturer[10]} \n"
                    f"Status : {lecturer[11]} \n\n"
                    f"Email : {lecturer[12]} \n"
                    f"Nomor Telepon : {lecturer[13]} \n\n"
                    f"=================================== \n\n"
                )
            if not lecturers:
                fulfillment_text += "Tidak ada data dosen yang tersedia saat ini."
        elif information_item == "Profil Prodi" or information_item == "Deskripsi Profil":
            profile_data = db_helper.get_profile()
            fulfillment_text = (
                f"Baik, Berikut adalah Profil Prodi Sistem Informasi : \n\n"
                f"Program Studi : {profile_data[1]} \n"
                f"Fakultas : {profile_data[2]} \n"
                f"Universitas : {profile_data[3]} \n"
                f"Tipe Program : {profile_data[4]} \n"
                f"Akreditasi : {profile_data[5]} \n"
                f"Durasi Studi : {profile_data[6]} \n"
                f"Visi : {profile_data[7]} \n"
                f"Misi : {profile_data[8]} \n"
                f"Kompetensi Lulusan : {profile_data[9]} \n"
                f"Keterangan : {profile_data[10]} \n"
            )
        elif information_item == "Pengumuman":
            announcements = db_helper.get_newest_announcements()
            fulfillment_text = (
                f"Baik, Berikut adalah Pengumuman Terbaru : \n\n"
                f"Kode Pengumuman : {announcements[1]} \n"
                f"Judul Pengumuman : {announcements[2]} \n"
                f"Tanggal Pengumuman : {announcements[3]} \n"
                f"Kategori Pengumuman : {announcements[4]} \n"
                f"Penerbit Pengumuman : {announcements[5]} \n"
                f"Deskripsi Pengumuman : {announcements[6]} \n"
                f"Link Pengumuman : {announcements[7]} \n\n"
            )
            # sent follow up message to ask for more information
            fulfillment_text += (
                f"Apakah Kakak ingin mencari Pengumuman yang lebih lebih spesifik ?\n"
                f"Jika IYA, saya bisa membantu mencari dengan menyesuaikan kategori pengumumannya !! :D \n\n"
                f"Silahkan kiriimkan pesan seperti ini ya... \"Saya ingin mencari pengumuman dengan kategori Perkuliahan\" \n"
                f"Maka saya bisa mengeluarkan seluruh pengumuman yang termasuk kedalam kategori tersebut :D !\n"
            )    
        elif information_item == "Panduan Pembayaran":
            payment_guide = db_helper.get_payment_guide()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Panduan Pembayaran : \n\n"
            )  
            for guide in payment_guide:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Judul Panduan : {guide[1]} \n"
                    f"Deskripsi Panduan : {guide[2]} \n"
                    f"Kategori Panduan Pembayaran: {guide[3]} \n"
                    f"Angkatan : {guide[4]} \n"
                    f"Tahun : {guide[5]} \n"
                    f"Link Panduan : {guide[6]} \n "
                    f"=================================== \n\n"
                )
            if not payment_guide:
                fulfillment_text += "Tidak ada data panduan pembayaran yang tersedia saat ini."
        elif information_item == "Jadwal Pembayaran":
            payment_schedule = db_helper.get_payment_schedule()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Jadwal Pembayaran : \n\n"
            )

            for schedule in payment_schedule:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Judul : {schedule[1]} \n"
                    f"Penerbit : {schedule[2]} \n"
                    f"Penerima : {schedule[3]} \n"
                    f"Tahap : {schedule[4]} \n"
                    f"Sejak : {schedule[5]} \n"
                    f"Sampai : {schedule[6]} \n "
                    f"Keterangan : {schedule[7]} \n "
                    f"Link : {schedule[8]} \n "
                    f"=================================== \n\n"
                )
            if not payment_schedule:
                fulfillment_text += "Tidak ada data jadwal pembayaran yang tersedia saat ini."
        elif information_item == "Berkas Akademik":
            files = db_helper.get_files()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Berkas Akademik : \n\n"
            )

            for file in files:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Kode : {file[1]} \n"
                    f"Judul : {file[2]} \n"
                    f"Tanggal : {file[3]} \n"
                    f"Deskripsi : {file[4]} \n"
                    f"Link : {file[5]} \n"
                    f"=================================== \n\n"
                )   

            if not files:
                fulfillment_text += "Tidak ada data berkas akademik yang tersedia saat ini."
        elif information_item == "Syarat Skripsi":
            skripsiRequisites = db_helper.get_skripsi_requisites()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Syarat Skripsi : \n\n"
            )

            for requisite in skripsiRequisites:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Kode : {requisite[1]} \n"
                    f"Judul : {requisite[2]} \n"
                    f"Deskripsi : {requisite[3]} \n"
                    f"Link : {requisite[4]} \n"
                    f"=================================== \n\n"
                )
            if not skripsiRequisites:
                fulfillment_text += "Tidak ada data syarat skripsi yang tersedia saat ini."
        elif information_item == "Panduan Skripsi":
            skripsiGuides = db_helper.get_skripsi_guides()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Panduan Skripsi : \n\n"
            )

            for guide in skripsiGuides:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Kode : {guide[1]} \n"
                    f"Judul : {guide[2]} \n"
                    f"Deskripsi : {guide[3]} \n"
                    f"Link : {guide[4]} \n"
                    f"=================================== \n\n"
                )
            if not skripsiGuides:
                fulfillment_text += "Tidak ada data panduan skripsi yang tersedia saat ini."
        elif information_item == "Syarat Kerja Praktek":
            internRequisites = db_helper.get_internship_requisites()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Syarat Kerja Praktek : \n\n"
            )

            for requisite in internRequisites:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Kode : {requisite[1]} \n"
                    f"Judul : {requisite[2]} \n"
                    f"Deskripsi : {requisite[3]} \n"
                    f"Link : {requisite[4]} \n"
                    f"=================================== \n\n"
                )

            if not internRequisites:
                fulfillment_text += "Tidak ada data syarat kerja praktek yang tersedia saat ini."
        elif information_item == "Panduan Kerja Praktek":
            internGuides = db_helper.get_internship_guides()
            fulfillment_text = (
                f"Baik, Berikut adalah Informasi Panduan Kerja Praktek : \n\n"
            )

            for guide in internGuides:
                # fetch all the data and append it to the fulfillment text
                fulfillment_text += (
                    f"=================================== \n"
                    f"Kode : {guide[1]} \n"
                    f"Judul : {guide[2]} \n"
                    f"Deskripsi : {guide[3]} \n"
                    f"Link : {guide[4]} \n"
                    f"=================================== \n\n"
                )
            if not internGuides:
                fulfillment_text += "Tidak ada data panduan kerja praktek yang tersedia saat ini."
        else:
            fulfillment_text = "Maaf, sepertinya informasi yang kamu minta belum tersedia... \n\nSilahkan pilih informasi yang tersedia ya :D."
    else:
        fulfillment_text = "Maaf, sepertinya kamu belum terdaftar... \n\nSilahkan kirimkan NIM kamu ya :D."
        output_contexts = [
            {
                "name": "projects/bantusi-ukoi/agent/sessions/55efc5a7-6194-8da9-896a-0f9790062aa2/contexts/defaultwelcomeintent-followup",
                "lifespanCount": 2,
            }
        ]
        
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })
    
def track_subject(parameters: dict):
    subject_code = parameters["subject-code"]
    subject_data = db_helper.get_subjects(subject_code)

    if subject_data:
        fulfillment_text = (
            f"Berikut adalah informasi mengenai mata kuliah {subject_data[2]} dengan Kode {subject_code} : \n\n"
            f"Nama Mata Kuliah : {subject_data[2]} \n"
            f"Jenis Kelas : {subject_data[3]} \n"
            f"SKS : {subject_data[4]} \n"
            f"Dosen : {subject_data[5]} \n"
            f"Hari : {subject_data[6]} \n"
            f"Waktu : {subject_data[7]} \n"
            f"Link V-Class : {subject_data[8]} \n"
            f"Kode Enrollment : {subject_data[9]} \n"
            f"Link Group Mata Kuliah : {subject_data[10]} \n"
        )
    else:
        fulfillment_text = "Maaf, sepertinya Kode Mata Kuliah yang kamu masukkan salah atau tidak terdaftar... \n\nSilahkan kirimkan ulang Kode Mata Kuliah kamu atau hubungi bagian administrasi ya :D."

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })
       
def track_announcements(category :dict):
    category = category["announcement_categories"]
    announcements = db_helper.get_announcements_with_category(category)
    fulfillment_text = (
        f"Berikut adalah Pengumuman dengan Kategori {category} : \n\n"
    )
    for announcement in announcements:
        # fetch all the data and append it to the fulfillment text
        fulfillment_text += (
            f"=================================== \n\n"
            f"Kode Pengumuman : {announcement[1]} \n"
            f"Judul Pengumuman : {announcement[2]} \n"
            f"Tanggal Pengumuman : {announcement[3]} \n"
            f"Kategori Pengumuman : {announcement[4]} \n"
            f"Penerbit Pengumuman : {announcement[5]} \n"
            f"Deskripsi Pengumuman : {announcement[6]} \n"
            f"Link Pengumuman : {announcement[7]} \n\n"
            f"=================================== \n\n"
        )
    if not announcements:
        fulfillment_text += "Maaf, sepertinya tidak ada pengumuman dengan kategori tersebut saat ini..."
        
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text,
    })