window.addEventListener("DOMContentLoaded", function () {
    showPage("global");
    const header = document.querySelector(".fixed-head");
    if (header) {
    const headerHeight = header.offsetHeight;
    document.body.style.marginTop = headerHeight + "px";
    }
});

function showPage(name) {
    document.querySelectorAll('.page-section').forEach(section => {
    section.style.display = 'none';
    });
    const activePage = document.getElementById("page_" + name);
    
    if (activePage) {
        if (name === 'car') {
            activePage.style.display = 'flex';
        } else {
            activePage.style.display = 'block';
        }
    }

    document.querySelectorAll('.page-button').forEach(btn => {
    btn.classList.remove('active-button');
    });
    const activeBtn = document.getElementById("btn_" + name);
    if (activeBtn) activeBtn.classList.add('active-button');
}

fetch("/diagnostic")
.then(res => res.json())
.then(infoDiagnostic => console.table(infoDiagnostic));

async function getData() {
    try {
    const res = await fetch("/race_dump_info");
    const data = await res.json();

    updateData(data);
    
    } catch (err) {
    console.error("Erreur lors de la récupération des données:", err);
    }    
}

setInterval(getData, 50);

function updateData(data){
    // All pages
    fetchWarnCarInFront(data);
    fetchWarnCarBehind(data);
    fetchCurrentFlag(data);
    // Page 1
    fetchBasicRaceInfo(data);
    fetchRace_Status(data);
    fetchSectorTimes(data);
    fetchLeaderboard(data);
    updateLapGraph(data);
    fetchWeather_Status(data);
    fetchWind_Status(data);
    // Page 2
    fetchCar_Infos(data);
    fetchCar_Data(data);
    fetchBrakes_Data(data);
    updateBrakeGraph(data);
    // Page 3
    updateDriverGraph(data);
    // Page 4
    fetchTire_Data(data);
}

// ----------------------- Warn Cars Around --------------------------- //
function fetchWarnCarInFront(data) {
    if (data.warn_infront === "True") {
        const alertBox = document.createElement("div");
        alertBox.className = "car-warning-box-in-front";

        if (data.nbr_veih_infront > 1){
        const message = `${data.veih_clother_infront} (${data.cat_clother_infront}) is ${Math.round(data.max_dist_infront)}m in front with ${data.nbr_veih_infront} other faster cars`;
        alertBox.textContent = message;
        }
        else {
        const message = `${data.veih_clother_infront} (${data.cat_clother_infront}) is ${Math.round(data.max_dist_infront)}m in front`;
        alertBox.textContent = message;
        }
        

        const container = document.querySelector(".car_in_front");
        container.innerHTML = "";

        container.appendChild(alertBox);
    }
    else{
        const container = document.querySelector(".car_in_front");
        container.innerHTML = "";
    }
}

async function fetchWarnCarBehind(data) {
    if (data.warn_behind === "True") {
        const alertBox = document.createElement("div");
        alertBox.className = "car-warning-box-behind";

        if (data.nbr_veih_behind > 1){
        const message = `${data.veih_clother_behind} (${data.cat_clother_behind}) is ${Math.round(data.max_dist_behind)}m behind with ${data.nbr_veih_behind} other faster cars`;
        alertBox.textContent = message;
        }
        else {
        const message = `${data.veih_clother_behind} (${data.cat_clother_behind}) is ${Math.round(data.max_dist_behind)}m behind`;
        alertBox.textContent = message;
        }
        

        const container = document.querySelector(".car_behind");
        container.innerHTML = "";

        container.appendChild(alertBox);
    }
    else{
        const container = document.querySelector(".car_behind");
        container.innerHTML = "";
    }
}

// ----------------------- Display Flag --------------------------- //
async function fetchCurrentFlag(data) {
    const flagElement = document.getElementById("flagDisplay");
    const flagBox = document.querySelector(".flag-box");

    if (data.RF2_running === "False" | data.pluginInjected === "False") {
        flagElement.textContent = "LMU not running or Shared Memory Plugin not/badly injected";
        flagElement.style.color = "red";
        flagBox.style.backgroundColor = "lightgray";
        return;
    }

    const flag = data.currentFlag;
    flagElement.textContent = `${flag}`;

    switch (flag) {
        case "GREEN":
        flagElement.style.color = "white";
        flagBox.style.backgroundColor = "green";
        break;
        case "BLUE":
        flagElement.style.color = "white";
        flagBox.style.backgroundColor = "blue";
        break;
        case "FYC":
        flagElement.style.color = "black";
        flagBox.style.backgroundColor = "yellow";
        break;
        case "DSQ":
        flagElement.style.color = "black";
        flagBox.style.backgroundColor = "white";
        break;
        case "NOTHING":
        flagElement.style.color = "black";
        flagBox.style.backgroundColor = "magenta";
        break;
        default:
        flagElement.style.color = "black";
        flagBox.style.backgroundColor = "gray";
        break;
    }
}

// ----------------------- Practice Page --------------------------- //

window.addEventListener("DOMContentLoaded", () => {
    fetch("/status")
    .then(res => res.json())
    .then(data => {

        if (data.running && data.program) {
        const container = document.querySelector(".practice_allprogs");
        const boxes = document.querySelectorAll(".practice_allprogs > .gray-box");

        const activeBox = boxes[data.program - 1];

        const statusElem = activeBox.querySelector(".status_prog");

        container.classList.add("expanded-mode");
        activeBox.classList.add("fullscreen");
        statusElem.textContent = `🟢 Programme ${data.program} lancé`;

        boxes.forEach(box => {
            if (box !== activeBox) {
            box.classList.add("hidden");
            }
        });
        }
    });
});

document.querySelectorAll(".prog_start_button").forEach((btn, index) => {
    btn.addEventListener("click", () => {
    const programNumber = index + 1;
    const currentBox = btn.closest(".gray-box");
    const container = document.querySelector(".practice_allprogs");

    fetch(`/toggle?program=${programNumber}`)
        .then(res => res.text())
        .then(msg => {
        const statusElement = currentBox.querySelector(".status_prog");
        statusElement.textContent = msg;

        if (msg.includes("🟢")) {
            container.classList.add("expanded-mode");
            currentBox.classList.add("fullscreen");

            document.querySelectorAll(".gray-box").forEach(box => {
            if (box !== currentBox) {
                box.classList.add("hidden");
            }
            });
        } else if (msg.includes("🔴")) {
            container.classList.remove("expanded-mode");
            currentBox.classList.remove("fullscreen");

            document.querySelectorAll(".gray-box").forEach(box => {
            box.classList.remove("hidden");
            });
        }
        });
    });
});


// ----------------------- Global Page --------------------------- //
async function fetchBasicRaceInfo(data) {
    if (data.RF2_running === false) {
        document.getElementById("basic_race_info").innerHTML = `
        <div><strong>Please, lauch LMU</strong></div><br>
        `;
    } else {
        document.getElementById("basic_race_info").innerHTML = `
        <div><strong>Current Session:</strong> ${data.sessionType}</div><br>
        <div><strong>Track Name:</strong> ${data.trackName}</div><br>
        <div><strong>Vehicule Name:</strong> ${data.vehicleName}</div><br>
        <div><strong>Driver Name:</strong> ${data.driverName}</div><br>
        `;
    }
}

async function fetchRace_Status(data) {
    const delta = data.last_lap - data.best_lap;
    let deltaColor = "gray";
    if (delta < 0) deltaColor = "rgb(0, 170, 0)";
    else if (delta > 0) deltaColor = "rgb(170, 0, 0)";
    let bestLapDisplay = typeof data.best_lap === "number" ? `${data.best_lap.toFixed(3)} s` : `${data.best_lap}`;
    let lastLapDisplay = typeof data.last_lap === "number" ? `${data.last_lap.toFixed(3)} s` : `${data.last_lap}`;
    let deltaDisplay = typeof data.delta_last_lap === "number"
        ? `<span style="color:${deltaColor}">${data.delta_last_lap.toFixed(3)} s</span>`
        : `<span>${data.delta_last_lap}</span>`;


    document.getElementById("race_status").innerHTML = `
        <strong>Lap:</strong> ${data.lap}/${data.total_laps}<br>
        <strong>Position:</strong> ${data.position}<br>
        <strong>Best Lap:</strong> ${bestLapDisplay}<br>
        <strong>Last Lap:</strong> ${lastLapDisplay}<br>
        <strong>Delta Last Lap:</strong> ${deltaDisplay}<br>
    `;
}

async function fetchSectorTimes(data) {
    const sectors = [
        { name: "Sector 1", current: data.sector1, best: data.best_sector1 },
        { name: "Sector 2", current: data.sector2, best: data.best_sector2 },
        { name: "Sector 3", current: data.sector3, best: data.best_sector3 }
    ];

    let html = "<table><tr><th>Secteur</th><th>Temps</th></tr>";

    sectors.forEach((s, i) => {
        let color = "gray";
        if (s.current === 0) {
        html += `<tr><td>${s.name}</td><td style="color:${color}">En cours</td></tr>`;
        return;
        }

        if (s.current < s.best) color = "purple";
        else if (s.current === s.best) color = "green";
        else color = "gold";

        if (typeof s.current === "number") {
        html += `<tr><td>${s.name}</td><td style="color:${color}">${s.current.toFixed(3)} s</td></tr>`;
        } else {
        html += `<tr><td>${s.name}</td><td style="color:${color}">${s.current}</td></tr>`;
        }
    });

    html += "</table>";
    document.getElementById("sectorTable").innerHTML = html;
}


async function fetchLeaderboard(data) {
    const tbody = document.querySelector("#leaderboard tbody");
    tbody.innerHTML = "";

    data.leaderboard.forEach(driver => {
        const row = document.createElement("tr");

        if (driver.name === data.driverName) {
            row.style.backgroundColor = "rgb(75, 75, 75, 1)";
        }

        row.innerHTML = `
        <td>${driver.place}</td>
        <td>${driver.name}</td>
        <td>${driver.category}</td>
        <td style="font-size: 12px">${driver.vehicle}</td>
        <td>${driver.laps}</td>
        <td>+${driver.behind}</td>
        <td>${driver.interval === 0 ? "-" : "+" + driver.interval}</td>
        `;
        tbody.appendChild(row);
    });
}

async function updateLapGraph(data) {
    const currentLap = data.lap;
    const lapTime = data.last_lap;
    const bestLap = data.best_lap;

    if (!lapChart.data.labels.includes("Lap " + currentLap) && lapTime > 0) {
    lapChart.data.labels.push("Lap " + currentLap);
    lapChart.data.datasets[0].data.push(lapTime);

    lapChart.data.datasets[1].data.push(bestLap);
    }

    lapChart.update();
}

const ctx = document.getElementById('driverChart').getContext('2d');

const lapChart = new Chart(ctx, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Current Lap Time',
        data: [],
        borderColor: 'rgba(0, 200, 255, 1)',
        backgroundColor: 'rgba(0, 200, 255, 0.2)',
        tension: 0.3,
        fill: false
        },
        {
        label: 'Best Lap Time',
        data: [],
        borderColor: 'rgba(100, 0, 0, 1)',
        backgroundColor: 'rgba(100, 0, 0, 0.2)',
        tension: 0.3,
        fill: false
        }
    ]
    },
    options: {
    responsive: true,
    animation: false,
    scales: {
        x: { title: { display: true, text: 'Tour' } },
        y: { title: { display: true, text: 'Temps (s)' } }
    }
    }
});

async function fetchWeather_Status(data) {
    document.getElementById("weather_data").innerHTML = `
        <div class="weather-item"><strong>Rain Severity:</strong> <span>${data.raining}%</span></div>
        <div class="weather-item"><strong>Min Path Wetness:</strong> <span>${data.minPathWetness}%</span></div>
        <div class="weather-item"><strong>Max Path Wetness:</strong> <span>${data.maxPathWetness}%</span></div>
        <div class="weather-item"><strong>Cloud Darkness:</strong> <span>${data.darkCloud}%</span></div>
        <div class="weather-item"><strong>Ambiant Temperature:</strong> <span>${data.ambiantTemp}°C</span></div>
        <div class="weather-item"><strong>Track Temperature:</strong> <span>${data.trackTemp}°C</span></div>
    `;
}

async function fetchWind_Status(data) {
    document.getElementById("wind_data").innerHTML = `
        <div class="weather-item"><strong>Wind Speed:</strong> <span>${data.windSpeed} km/h</span></div>
        <div class="weather-item"><strong>Wind Direction:</strong> <span>${data.windDegre}°</span></div>
        <div class="weather-item"><strong>Wind Cardinal:</strong> <span>${data.windDirection}</span></div>
    `;
}

// ----------------------- Car Data --------------------------- //

async function fetchCar_Infos(data) {
    document.getElementById("car_infos").innerHTML = `
        <strong>Speed:</strong> ${data.speed} km/h<br>
        <strong>RPM:</strong> ${data.rpm}<br>
        <strong>Gear:</strong> ${data.gear}<br>
        <strong>Fuel:</strong> ${data.fuel}L<br>
        <strong>Headlights:</strong> ${data.headlights}<br>
        <strong>Front Tire:</strong> ${data.frontTireName}<br>
        <strong>Rear Tire:</strong> ${data.rearTireName}<br>
        <strong>Speed Limiter Available:</strong> ${data.speedLimiterAvailable}<br>
        <strong>Speed Limiter Status:</strong> ${data.speedLimiter}<br>
        <strong>Break Balance (Front/Rear):</strong> ${100-data.rearBreakBias}%/${data.rearBreakBias}%<br>
    `;
}

async function fetchCar_Data(data) {
    updateDamageMap(data);

    document.getElementById("car_data").innerHTML = `
        <strong>Ignition Status:</strong> ${data.ignitionStatus}<br>
        <strong>Oil Temperature:</strong> ${data.oilTemp}°C<br>
        <strong>Water Temperature:</strong> ${data.waterTemp}°C<br>
        <strong>Status Overheating:</strong> ${data.isOverheating}<br>
        <strong>Pressure Turbo:</strong> ${data.turboPressure}<br>
        <strong>Fuel Level:</strong> ${data.fuel}L / ${data.capacityTank}L<br>
        <strong>Fuel Used For Previous Lap:</strong> ${data.fuelUsedLastLap}<br>
        <strong>Average Fuel/Lap:</strong> ${data.fuelUsedAverage}<br>
        <strong>Estimated Laps Until Tank Empty:</strong> ${data.fuelEstimation}<br>
    `;
}

async function fetchBrakes_Data(data) {
    let cfrb = 100 / (data.front_Left_Break_Press + 0.0000000001)
    let crrb = 100 / (data.front_Left_Break_Press + 0.0000000001)
    document.getElementById("brakes_data").innerHTML = `
        <div><strong>Temperature :</strong><br>    FL : ${data.front_Left_Break_Temp}°C<br>    FR : ${data.front_Right_Break_Temp}°C<br>    RL : ${data.rear_Left_Break_Temp}°C<br>    RR : ${data.rear_Right_Break_Temp}°C</div>
        <div><strong>Pressure :</strong><br>    FL : ${data.front_Left_Break_Press * cfrb}<br>    FR : ${data.front_Right_Break_Press * cfrb}<br>    RL : ${data.rear_Left_Break_Press * crrb}<br>    RR : ${data.rear_Right_Break_Press * crrb}</div>
    `;
}

function updateDamageMap(data) {
    const zoneMap = {
    "F": data.F,
    "FL": data.FL,
    "CL": data.CL,
    "BL": data.BL,
    "R": data.R,
    "BR": data.BR,
    "CR": data.CR,
    "FR": data.FR
    };

    Object.entries(zoneMap).forEach(([id, value]) => {
    const el = document.getElementById(id);
    if (!el) return;

    el.classList.remove("low-damage", "med-damage", "high-damage");

    if (value > 1) {
        el.classList.add("high-damage");
    } else if (value > 0) {
        el.classList.add("med-damage");
    } else {
        el.classList.add("low-damage");
    }
    });
}


const maxPoints_bp = 20;
let tickCounter_bp = 0;

const ctxBrakePress_fl = document.getElementById('chartBPFL').getContext('2d');
const chartBPFL = new Chart(ctxBrakePress_fl, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Front Left Brake Pressure',
        data: [],
        borderColor: 'rgba(255, 255, 255, 1)',
        fill: false
        }
    ]
    },
    options: {
        responsive: false,
        scales: {
        y: {
            beginAtZero: true,
            max: 100,
        },
        }
    }
});

const ctxBrakePress_fr = document.getElementById('chartBPFR').getContext('2d');
const chartBPFR = new Chart(ctxBrakePress_fr, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Front Right Brake Pressure',
        data: [],
        borderColor: 'rgba(255, 255, 255, 1)',
        fill: false
        }
    ]
    },
    options: {
        responsive: false,
        scales: {
        y: {
            beginAtZero: true,
            max: 100,
        },
        }
    }
});

const ctxBrakePress_rl = document.getElementById('chartBPRL').getContext('2d');
const chartBPRL = new Chart(ctxBrakePress_rl, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Rear Left Brake Pressure',
        data: [],
        borderColor: 'rgba(255, 255, 255, 1)',
        fill: false
        }
    ]
    },
    options: {
        responsive: false,
        scales: {
        y: {
            beginAtZero: true,
            max: 100,
        },
        }
    }
});

const ctxBrakePress_rr = document.getElementById('chartBPRR').getContext('2d');
const chartBPRR = new Chart(ctxBrakePress_rr, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Rear Right Brake Pressure',
        data: [],
        borderColor: 'rgba(255, 255, 255, 1)',
        fill: false
        }
    ]
    },
    options: {
        responsive: false,
        scales: {
        y: {
            beginAtZero: true,
            max: 100,
        },
        }
    }
});

const ctxForce = document.getElementById('chartForce').getContext('2d');
let chartForce = new Chart(ctxForce, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Live G-Force',
            data: [{x: 0, y: 0}],
            backgroundColor: 'red',
            pointRadius: 6,
            pointHoverRadius: 8,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
            x: {
                min: -5,
                max: 5,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                title: { display: true, text: 'Latéral (G)' }
            },
            y: {
                min: -5,
                max: 5,
                grid: { color: 'rgba(255, 255, 255, 0.1)' },
                title: { display: true, text: 'Longitudinal (G)' }
            }
        },
        plugins: {
            legend: { display: false }
        }
    }
});


async function updateBrakeGraph(data) {
    if (data.status === "not ready") return;

    const bpfl = data.front_Left_Break_Press * (100 / (data.front_Left_Break_Press + 0.0000000001));
    const bpfr = data.front_Right_Break_Press * (100 / (data.front_Left_Break_Press + 0.0000000001));
    const bprl = data.rear_Left_Break_Press * (100 / (data.front_Left_Break_Press + 0.0000000001));
    const bprr = data.rear_Right_Break_Press * (100 / (data.front_Left_Break_Press + 0.0000000001));

    const label = ``;

    [chartBPFL, chartBPFR, chartBPRL, chartBPRR].forEach(chart => {
    chart.data.labels.push(label);
    });

    chartBPFL.data.datasets[0].data.push(bpfl);
    chartBPFR.data.datasets[0].data.push(bpfr);
    chartBPRL.data.datasets[0].data.push(bprl);
    chartBPRR.data.datasets[0].data.push(bprr);


    [chartBPFL, chartBPFR, chartBPRL, chartBPRR].forEach(chart => {
    while (chart.data.labels.length > maxPoints_bp) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(ds => ds.data.shift());
    }
    chart.update();
    });
}

async function updateForceGraph(data) {
    if (data.status === "not ready") return;
    const lat = data.latG;
    const long = data.longG;
    chartForce.data.datasets[0].data = [{x: lat, y: long}];
    chartForce.update();
}


// ----------------------- Page 3 : Driver Data --------------------------- //
const maxPoints = 100;
let tickCounter = 0;

const ctxThrottle = document.getElementById('chartThrottle').getContext('2d');
const ctxBrake = document.getElementById('chartBrake').getContext('2d');
const ctxCombined = document.getElementById('chartCombined').getContext('2d');
const ctxDirec = document.getElementById('chartDirec').getContext('2d');

const commonOptions = (minY, maxY, labelY) => ({
    responsive: true,
    animation: false,
    scales: {
    y: {
        min: minY,
        max: maxY,
        title: { display: true, text: labelY }
    },
    x: { display: false }
    }
});

const chartThrottle = new Chart(ctxThrottle, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Throttle Live (%)',
        data: [],
        borderColor: 'rgba(0, 200, 255, 1)',
        fill: false
        },
        {
        label: 'Throttle Filtered (%)',
        data: [],
        borderColor: 'rgba(150, 130, 255, 0.7)',
        borderDash: [5, 5],
        fill: false
        }
    ]
    },
    options: commonOptions(0, 100, 'Throttle (%)')
});

const chartBrake = new Chart(ctxBrake, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Brake Live (%)',
        data: [],
        borderColor: 'rgba(200, 0, 0, 1)',
        fill: false
        },
        {
        label: 'Brake Filtered (%)',
        data: [],
        borderColor: 'rgba(125, 75, 0, 0.8)',
        borderDash: [5, 5],
        fill: false
        }
    ]
    },
    options: commonOptions(0, 100, 'Frein (%)')
});

const chartCombined = new Chart(ctxCombined, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Throttle Live',
        data: [],
        borderColor: 'rgba(0, 200, 255, 1)',
        fill: false
        },
        {
        label: 'Brake Live',
        data: [],
        borderColor: 'rgba(200, 0, 0, 1)',
        fill: false
        },
        {
        label: 'Input on Wheel Live',
        data: [],
        borderColor: 'rgba(85, 150, 85, 1)',
        fill: false
        },
    ]
    },
    options: commonOptions(0, 100, "")
});

const chartDirec = new Chart(ctxDirec, {
    type: 'line',
    data: {
    labels: [],
    datasets: [
        {
        label: 'Input on Wheel Live',
        data: [],
        borderColor: 'rgba(0, 200, 0, 1)',
        fill: false
        },
        {
        label: 'Input Filtered',
        data: [],
        borderColor: 'rgba(166, 200, 0, 0.7)',
        borderDash: [5, 5],
        fill: false
        }
    ]
    },
    options: commonOptions(-1, 1, 'Direction (−1 ↔ +1)')
});

async function updateDriverGraph(data) {
    if (data.status === "not ready") return;

    const throttleLive = data.live_throttle * 100;
    const throttleSmooth = data.live_throttle_smooth * 100;
    const brakeLive = data.live_brake * 100;
    const brakeSmooth = data.live_brake_smooth * 100;
    const direcLive = data.live_direc;
    const direcSmooth = data.live_direc_smooth;

    const label = `t+${tickCounter++}`;

    [chartThrottle, chartBrake, chartCombined, chartDirec].forEach(chart => {
    chart.data.labels.push(label);
    });

    chartThrottle.data.datasets[0].data.push(throttleLive);
    chartThrottle.data.datasets[1].data.push(throttleSmooth);

    chartBrake.data.datasets[0].data.push(brakeLive);
    chartBrake.data.datasets[1].data.push(brakeSmooth);

    chartCombined.data.datasets[0].data.push(throttleLive);
    chartCombined.data.datasets[1].data.push(brakeLive);
    chartCombined.data.datasets[2].data.push((direcLive + 1) * 50);

    chartDirec.data.datasets[0].data.push(direcLive);
    chartDirec.data.datasets[1].data.push(direcSmooth);

    [chartThrottle, chartBrake, chartCombined, chartDirec].forEach(chart => {
    while (chart.data.labels.length > maxPoints) {
        chart.data.labels.shift();
        chart.data.datasets.forEach(ds => ds.data.shift());
    }
    chart.update();
    });
}

// ----------------------- Page 4 : Tire Data --------------------------- //
document.addEventListener("DOMContentLoaded", () => {
    initChartTire();
    bindEvents();
    fetchCarData(data);
    setInterval(fetchTire_Data, 500);
});

let chartTire = null;
const inputValues = {};

function initChartTire() {
    const ctxTire = document.getElementById('chartTire').getContext('2d');
    chartTire = new Chart(ctxTire, {
    type: 'line',
    data: {
        labels: [],
        datasets: [
        {
            label: 'Tire Simulation (%)',
            data: [],
            borderColor: "rgba(255, 255, 255, 1)",
            backgroundColor: "rgba(255, 255, 255, 0.2)",
            fill: true,
            yAxisID: 'y'
        },
        {
            label: 'Fuel Simulation (%)',
            data: [],
            borderColor: "rgba(206, 175, 127, 0.7)",
            fill: false,
            yAxisID: 'y'
        },
        {
            label: 'Estimated Lap Time (s)',
            data: [],
            borderColor: "rgba(150, 0, 255, 0.7)",
            fill: false,
            yAxisID: 'y1'
        }
        ]
    },
    options: {
        responsive: true,
        scales: {
        y: {
            type: 'linear',
            position: 'left',
            beginAtZero: true,
            max: 100,
            title: {
            display: true,
            text: 'Degradation / Fuel (%)'
            }
        },
        y1: {
            type: 'linear',
            position: 'right',
            beginAtZero: true,
            reverse: true,
            title: {
            display: true,
            text: 'Lap Time (s)'
            },
            grid: {
            drawOnChartArea: false
            }
        }
        }
    }

    });
}

const pace_array = [
    ["economy_pace", 0.7, 0],
    ["very_slow_pace", 0.8, 1],
    ["slow_pace", 0.9, 2],
    ["mid_pace", 1.0, 3],
    ["fast_pace", 1.1, 4],
    ["very_fast_pace", 1.2, 5],
    ["quali_pace", 1.3, 6]
];
const tire_array = [
    ["soft_tire", 1.2, 0.995, "rgba(200, 0, 0, 1)", "rgba(200, 0, 0, 0.05)"], ["medium_tire", 1, 1, "rgba(247, 206, 0, 1)", "rgba(247, 206, 0, 0.05)"], ["hard_tire", 0.8, 1.005, "rgba(255, 255, 255, 1)", "rgba(255, 255, 255, 0.05)"], ["wet_tire", 0.4, 1.08, "rgba(0, 140, 255, 1)", "rgba(0, 140, 255, 0.05)"]
];

function getSelectedRadioValue(name) {
    const selected = document.querySelector(`input[name="${name}"]:checked`);
    return selected ? selected.id : null;
}

function updateNumericInputs() {
    let filled = true;
    document.querySelectorAll('#page_tire input[type="number"]').forEach(input => {
    const id = input.id;
    const value = input.value;
    if (value === "") filled = false;
    inputValues[id] = value !== "" ? parseFloat(value) : null;
    });
    const waterInput = document.getElementById("thickness");
    inputValues["water_thickness"] = waterInput ? parseFloat(waterInput.value) : 0;

    if (filled) updateTireSimulation();
}

let dead_car_lap = 0
function updateTireSimulation() {
    const result = usage_Coef();
    if (!result || isNaN(result.coef)) return;

    const { coef, tirecolor, backgroundtirecolor, tire_compound, pace } = result;
    const laps = 70;
    const labels = Array.from({ length: laps }, (_, i) => `Lap ${i + 1}`);
    const datafuel = [];
    let datatire = [];
    const paceId = getSelectedRadioValue("pace");
    const paceEntry = pace_array.find(([id]) => id === paceId);
    const paceFactor = paceEntry?.[1] ?? 1;

    let dead_tire_lap = 0
    let tireWear = 100;
    while (tireWear > 0) {
    tireWear -= coef;
    datatire.push(Math.max(tireWear, 0));
    dead_tire_lap += 1;
    }

    chartTire.data.labels = labels;
    chartTire.data.datasets[0].data = datatire;
    chartTire.data.datasets[0].borderColor = tirecolor;
    chartTire.data.datasets[0].backgroundColor = backgroundtirecolor;
    chartTire.update();

    let fuellevel = inputValues["fuelselected"];
    const fuelCapacity = inputValues["capacityTank"];

    let dead_fuel_lap = 0;
    console.log(inputValues)
    while (fuellevel > 0) {
    fuellevel -= ((inputValues["prog_fuel_used"] * 100) / fuelCapacity) * paceFactor;
    datafuel.push(Math.max(fuellevel, 0));
    dead_fuel_lap += 1;
    }
    if (dead_tire_lap < dead_fuel_lap) {
    dead_car_lap = dead_tire_lap;
    } else {
    dead_car_lap = dead_fuel_lap;
    };
    calcul_estimated_laptime();
    chartTire.data.labels = labels;
    chartTire.data.datasets[1].data = datafuel;
    chartTire.update();
}


function usage_Coef() {
    const paceId = getSelectedRadioValue("pace");
    const tireId = getSelectedRadioValue("typetire");

    const paceEntry = pace_array.find(([id]) => id === paceId);
    const tireEntry = tire_array.find(([id]) => id === tireId);

    const tirecolor = tireEntry?.[3] ?? null;
    const backgroundtirecolor = tireEntry?.[4] ?? null;
    const pace = paceEntry?.[1] ?? null;
    const tire_compound = tireEntry?.[1] ?? null;

    const fl = inputValues["prog_tire_degradation_fl"];
    const fr = inputValues["prog_tire_degradation_fr"];
    const rl = inputValues["prog_tire_degradation_rl"];
    const rr = inputValues["prog_tire_degradation_rr"];

    if ([fl, fr, rl, rr].some(v => typeof v !== "number")) return null;
    if (pace === null || tire_compound === null) return null;

    const coef_degradation = (fl + fr + rl + rr) / 4;
    const coef = coef_degradation * pace * tire_compound;

    return { coef, tirecolor, backgroundtirecolor, tire_compound, pace };
}

function calcul_estimated_laptime () {
    const laps = 70;
    const labels = Array.from({ length: laps }, (_, i) => `Lap ${i + 1}`);
    const paceId = getSelectedRadioValue("pace");
    const tireId = getSelectedRadioValue("typetire");
    const datatime = [];
    const paceEntry = pace_array.find(([id]) => id === paceId);
    const tireEntry = tire_array.find(([id]) => id === tireId);

    const avglap = inputValues["prog_avg_lap_time"];
    const qualilap = inputValues["prog_quali_lap_time"];
    const tire_compound = tireEntry?.[2] ?? null;
    const pace = paceEntry?.[2] ?? null;
    
    const scale = avglap-qualilap
    let list_laptime_estimated = [/*Eco*/avglap+scale, /*VS*/avglap*1.021,  /*S*/avglap*1.008, /*R*/avglap, /*F*/avglap*0.992, /*VF*/avglap*0.979, /*Quali*/qualilap]
    let list_laptime_estimated_TEST = [/*Eco*/(avglap+scale)*tire_compound, /*VS*/(avglap+((scale/4)*2))*tire_compound,  /*S*/(avglap+(scale/4))*tire_compound, /*R*/avglap*tire_compound, /*F*/(avglap-(scale/4))*tire_compound, /*VF*/(avglap-((scale/4)*2))*tire_compound, /*Quali*/qualilap*tire_compound]
    const waterThickness = inputValues["water_thickness"] ?? 0;

    let k = 0;
    while (k < dead_car_lap) {
    let adjustedTire = avglap + 0.5 * (Math.exp(0.1*k) - 1)
    datatime.push(Math.max(adjustedTire, 0));
    k += 1
    }
    datatime.push(Math.max(10000000, 0));

let minLapTime, maxLapTime;
/*
if (tireEntry?.[0] === "wet_tire") {
    const rawMin = avglap + 30;
    const rawMax = qualilap + 10;
    minLapTime = Math.min(rawMin, rawMax);
    maxLapTime = Math.max(rawMin, rawMax);
} else {
    const rawMin = avglap + 10;
    const rawMax = qualilap * 0.995;
    minLapTime = Math.min(rawMin, rawMax);
    maxLapTime = Math.max(rawMin, rawMax);
}

minLapTime *= 1 + 0.005 * Math.pow(waterThickness, 1.2);
maxLapTime *= 1 + 0.005 * Math.pow(waterThickness, 1.2);
*/
chartTire.options.scales.y1.min = avglap;
chartTire.options.scales.y1.max = avglap + 50;
chartTire.options.scales.y1.reverse = true;

chartTire.data.labels = labels;
chartTire.data.datasets[2].data = datatime;
chartTire.update();
}

function bindEvents() {
    document.getElementById("fuelselected").addEventListener("input", updateNumericInputs);
    document.getElementById("thickness").addEventListener("input", updateNumericInputs);
    document.querySelectorAll('input[type="radio"][name="pace"], input[type="radio"][name="typetire"]').forEach(radio => {
    radio.addEventListener('change', () => {
        inputValues[radio.id] = true;
        updateNumericInputs();
    });
    });

    document.querySelectorAll('.inputs_category input[type="number"]').forEach(input => {
    input.addEventListener('input', updateNumericInputs);
    });

    document.querySelector('button').addEventListener('click', updateNumericInputs);
}

async function fetchCarData(data) {
    inputValues["fuel_capacity"] = data.capacityTank;
}

async function fetchTire_Data(data) {
    updateDamageTire(data);
    updateTempTire(data);
    updatePressTire(data);
    updateFlatTire(data);
}

function updateDamageTire(data) {
    const zoneMap = {
    "average": { label: "Average Usure = ", value: (data.front_Left_Wear + data.front_Right_Wear + data.rear_Left_Wear + data.rear_Right_Wear) / 4 },
    "front_Left_Wear": { label: "Front Left Tire Usure = ", value: data.front_Left_Wear },
    "front_Right_Wear": { label: "Front Right Tire Usure = ", value: data.front_Right_Wear },
    "rear_Left_Wear": { label: "Rear Left Tire Usure = ", value: data.rear_Left_Wear },
    "rear_Right_Wear": { label: "Rear Right Tire Usure = ", value: data.rear_Right_Wear },
    };

    Object.entries(zoneMap).forEach(([id, info]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = `${info.label} ${(info.value * 100).toFixed(2)}%`;
    });
}

function updateTempTire(data) {
    const zone_temp = {
    "front_Left_Temp": { label: "Front Left Tire Temperature = ", value: data.front_Left_Temp },
    "front_Right_Temp": { label: "Front Right Tire Temperature = ", value: data.front_Right_Temp },
    "rear_Left_Temp": { label: "Rear Left Tire Temperature = ", value: data.rear_Left_Temp },
    "rear_Right_Temp": { label: "Rear Right Tire Temperature = ", value: data.rear_Right_Temp },
    };

    Object.entries(zone_temp).forEach(([id, info]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = `${info.label} ${info.value.toFixed(2)}`;
    });
}

function updatePressTire(data) {
    const zone_press = {
    "front_Left_Pressure": { label: "Front Left Tire Pressure (bar) = ", value: data.front_Left_Pressure },
    "front_Right_Pressure": { label: "Front Right Tire Pressure (bar) = ", value: data.front_Right_Pressure },
    "rear_Left_Pressure": { label: "Rear Left Tire Pressure (bar) = ", value: data.rear_Left_Pressure },
    "rear_Right_Pressure": { label: "Rear Right Tire Pressure (bar) = ", value: data.rear_Right_Pressure },
    };

    Object.entries(zone_press).forEach(([id, info]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = `${info.label} ${info.value.toFixed(2)}`;
    });
}

function updateFlatTire(data) {
    const zone_flat = {
    "front_Left_Flat": { label: "Front Left Tire Flat = ", value: data.front_Left_Flat },
    "front_Right_Flat": { label: "Front Right Tire Flat = ", value: data.front_Right_Flat },
    "rear_Left_Flat": { label: "Rear Left Tire Flat = ", value: data.rear_Left_Flat },
    "rear_Right_Flat": { label: "Rear Right Tire Flat = ", value: data.rear_Right_Flat },
    };

    Object.entries(zone_flat).forEach(([id, info]) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = `${info.label}`;
    });
}

/* To add : G Forces, tc, abs, stab ctrl, switch of background image */
/* To do : fix brake press*/