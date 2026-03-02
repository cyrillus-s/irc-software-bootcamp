#  Creative Drone Mission – Pentagon Pattern (DroneKit SITL)

## Deskripsi Umum Misi

Misi ini dirancang menggunakan DroneKit untuk dijalankan pada Mission Planner SITL. 
Alur dasar yang diimplementasikan adalah:

ARM → TAKEOFF → MAJU → HOVER → POLA SEGI LIMA 3D → MUNDUR → LANDING

Namun misi ini dikembangkan menjadi lebih kompleks dengan variasi ketinggian, hover di beberapa titik, serta monitoring telemetry secara paralel.

---

##  Pola Terbang

Misi dimulai dengan proses arm dan takeoff hingga ketinggian 10 meter sebagai fase stabilisasi awal. Setelah mencapai altitude target, drone bergerak maju sejauh 15 meter ke arah utara dan melakukan hover selama beberapa detik.

Bagian inti dari misi adalah pembentukan pola segi lima beraturan dengan radius sekitar 20 meter. Drone bergerak melalui lima titik berdasarkan sudut:

0°, 72°, 144°, 216°, dan 288°

Setiap waypoint memiliki variasi ketinggian:
- 12 meter
- 15 meter
- 18 meter
- 14 meter
- 10 meter

Dengan demikian lintasan yang terbentuk bukan hanya dua dimensi, tetapi tiga dimensi karena terdapat perubahan altitude di setiap titik. Setelah menyelesaikan satu putaran penuh dan hover di tiap waypoint, drone bergerak mundur 15 meter sebelum masuk ke mode LAND untuk pendaratan otomatis.

---

##  Fungsi-Fungsi yang Digunakan

Beberapa fungsi penting dalam skrip ini antara lain:

### 1. switch_mode()
Berfungsi untuk mengganti flight mode dan memastikan mode benar-benar aktif sebelum eksekusi berikutnya dijalankan. Hal ini mencegah race condition.

### 2. arm_and_takeoff()
Mengatur proses pre-flight, termasuk:
- Mengecek apakah drone armable
- Mengubah mode ke GUIDED
- Arming motor
- Takeoff ke altitude target
- Monitoring ketinggian hingga tercapai

### 3. get_offset_location()
Mengubah pergeseran dalam meter (North-East) menjadi koordinat GPS baru (latitude-longitude). Fungsi ini penting karena navigasi DroneKit berbasis koordinat global.

### 4. goto_offset()
Fungsi navigasi utama yang:
- Mengirim drone ke target menggunakan simple_goto()
- Memonitor jarak hingga threshold tercapai
- Mengatur waktu hover di waypoint

### 5. telemetry_worker() (Thread)
Berjalan secara paralel untuk membaca data altitude dan battery setiap beberapa detik tanpa mengganggu misi utama.

### 6. attitude_callback()
Listener yang membaca perubahan attitude (roll, pitch, yaw) secara real-time untuk monitoring dinamika orientasi drone.

---

## Mode yang Digunakan

### GUIDED
Digunakan selama seluruh fase navigasi karena memungkinkan kontrol penuh melalui kode (simple_takeoff dan simple_goto).

### LAND
Digunakan pada tahap akhir untuk pendaratan otomatis yang lebih aman dan stabil karena dikontrol langsung oleh flight controller.

---

## Tantangan dan Solusi

Beberapa tantangan yang ditemui dalam perancangan misi ini:

1. Waypoint relatif dapat menyebabkan drift posisi  
   Solusi: Offset selalu dihitung berdasarkan posisi terkini drone.

2. Sinkronisasi altitude dan pergerakan horizontal  
   Solusi: Monitoring dilakukan terus menerus hingga jarak dan ketinggian memenuhi ambang batas.

3. Potensi konflik thread telemetry  
   Solusi: Thread hanya membaca data (read-only) sehingga tidak terjadi konflik penulisan data.

4. Race condition saat pergantian mode  
   Solusi: Menggunakan fungsi switch_mode() dengan sistem blocking wait.

---

## Pengembangan Selanjutnya

Jika dikembangkan lebih lanjut, misi ini dapat ditingkatkan dengan:

- Pola spiral 3D (ascending helix)
- Figure-8 pattern
- Kontrol yaw dinamis agar drone selalu menghadap pusat pola
- Failsafe berbasis level baterai (auto RTL)
- Logging telemetry ke file CSV untuk analisis pasca-flight

---

## Kesimpulan

Misi ini tidak hanya memenuhi alur dasar ARM, TAKEOFF, MAJU, MUNDUR, dan LANDING, tetapi juga mengintegrasikan pola geometris tiga dimensi, variasi ketinggian, serta monitoring sistem secara paralel.

Dengan pendekatan ini, sistem UAV tidak hanya bergerak berdasarkan perintah sederhana, tetapi berjalan secara terstruktur, terukur, dan mendekati implementasi sistem otonom yang lebih kompleks.

## Link Video Simulasi
https://drive.google.com/file/d/1ztvxYtGzOD68_c0h8mXOPhurqPxwgFGM/view?usp=sharing