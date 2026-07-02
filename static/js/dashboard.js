// =======================================================
// Charts
// =======================================================

const requestChart = new Chart(
    document.getElementById("requestChart"),
    {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Requests / sec",
                data: [],
                borderColor: "#37f5d4",
                tension: 0.3
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false
        }
    }
);

const latencyChart = new Chart(
    document.getElementById("latencyChart"),
    {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Latency",
                data: [],
                borderColor: "#ffd95b",
                tension: 0.3
            }]
        },
        options: {
            animation: false,
            responsive: true,
            maintainAspectRatio: false
        }
    }
);

// =======================================================
// Prevent Dashboard Polling
// from overwriting Chaos Controls
// =======================================================

let editingChaos = false;

[
    "failureRate",
    "minLatency",
    "maxLatency",
    "retryAttempts",
    "rateLimit"
].forEach(id => {

    const el = document.getElementById(id);

    if(!el) return;

    el.addEventListener("focus",()=>editingChaos=true);

    el.addEventListener("blur",()=>editingChaos=false);

});

// =======================================================
// Dashboard Polling
// =======================================================

async function updateDashboard(){

    const res=await fetch("/dashboard-data");

    const data=await res.json();

    const m=data.metrics;

    // ---------------- Cards ----------------

    document.getElementById("request-count").innerText=m.total_requests;

    document.getElementById("success-rate").innerText=
        m.success_rate+"%";

    document.getElementById("failure-count").innerText=
        m.failures;

    document.getElementById("latency").innerText=
        Math.round(m.average_latency_ms)+" ms";

    // ---------------- Boss ----------------

    document.getElementById("boss-hp").style.width=
        m.health+"%";

    document.getElementById("boss-status").innerText=
        m.system_status;

    // ---------------- Badge ----------------

    const badge=document.querySelector(".status");

    badge.innerText=m.system_status;

    if(m.system_status==="ONLINE")
        badge.style.background="#45ff7a";

    else if(m.system_status==="DEGRADED")
        badge.style.background="#ffd84a";

    else
        badge.style.background="#ff4040";

    // ---------------- Charts ----------------

    requestChart.data.labels.push("");

    requestChart.data.datasets[0].data.push(
        m.requests_per_second
    );

    if(requestChart.data.labels.length>30){

        requestChart.data.labels.shift();

        requestChart.data.datasets[0].data.shift();

    }

    requestChart.update();

    latencyChart.data.labels.push("");

    latencyChart.data.datasets[0].data.push(
        m.average_latency_ms
    );

    if(latencyChart.data.labels.length>30){

        latencyChart.data.labels.shift();

        latencyChart.data.datasets[0].data.shift();

    }

    latencyChart.update();

    // ---------------- Logs ----------------

    const logs=document.getElementById("logs");

    logs.innerHTML="";

    data.recent_logs
        .slice()
        .reverse()
        .forEach(log=>{

            logs.innerHTML+=`
            <p>
            [${log.timestamp.slice(11,19)}]
            ${log.status}
            •
            ${log.latency_ms}ms
            </p>`;

        });

    // ---------------- Chaos Controls ----------------

    if(!editingChaos){

        const chaos=await fetch("/chaos/current");

        const cfg=await chaos.json();

        document.getElementById("failureRate").value=cfg.failure_rate;
        document.getElementById("minLatency").value=cfg.min_latency;
        document.getElementById("maxLatency").value=cfg.max_latency;
        document.getElementById("retryAttempts").value=cfg.retry_attempts;
        document.getElementById("rateLimit").value=cfg.rate_limit;

        document.getElementById("failureValue").innerText=
            Math.round(cfg.failure_rate*100)+"%";

    }

}

setInterval(updateDashboard,1000);

updateDashboard();

// =======================================================
// Manual Requests
// =======================================================

async function sendRequests(count){

    const jobs=[];

    for(let i=0;i<count;i++)
        jobs.push(fetch("/data"));

    await Promise.allSettled(jobs);

}

document.getElementById("sendOne").onclick=()=>sendRequests(1);

document.getElementById("sendTen").onclick=()=>sendRequests(10);

document.getElementById("sendHundred").onclick=()=>sendRequests(100);

document.getElementById("chaosMode").onclick=()=>sendRequests(500);

// =======================================================
// Continuous Traffic
// =======================================================

let trafficLoop=null;

const slider=document.getElementById("trafficRate");

const value=document.getElementById("trafficValue");

slider.oninput=()=>{

    value.innerText=
        slider.value+" req/sec";

};

document.getElementById("startTraffic").onclick=()=>{

    if(trafficLoop) return;

    document.getElementById("trafficStatus").innerText="🟢 Running";

    trafficLoop=setInterval(()=>{

        sendRequests(Number(slider.value));

    },1000);

};

document.getElementById("stopTraffic").onclick=()=>{

    clearInterval(trafficLoop);

    trafficLoop=null;

    document.getElementById("trafficStatus").innerText="🔴 Idle";

};

// =======================================================
// Apply Chaos
// =======================================================

document.getElementById("failureRate").oninput=()=>{

    document.getElementById("failureValue").innerText=

        Math.round(

            document.getElementById("failureRate").value*100

        )+"%";

};

document.getElementById("applyChaos").onclick=async()=>{

    await fetch("/chaos/update",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({

            failure_rate:Number(document.getElementById("failureRate").value),

            min_latency:Number(document.getElementById("minLatency").value),

            max_latency:Number(document.getElementById("maxLatency").value),

            retry_attempts:Number(document.getElementById("retryAttempts").value),

            rate_limit:Number(document.getElementById("rateLimit").value)

        })

    });

    updateDashboard();

};

// =======================================================
// Reset Simulation
// =======================================================

document.getElementById("resetSim").onclick = async () => {

    // Stop continuous traffic
    if (trafficLoop) {
        clearInterval(trafficLoop);
        trafficLoop = null;
    }

    document.getElementById("trafficStatus").innerText = "🔴 Idle";

    // Clear request chart
    requestChart.data.labels = [];
    requestChart.data.datasets[0].data = [];
    requestChart.update();

    // Clear latency chart
    latencyChart.data.labels = [];
    latencyChart.data.datasets[0].data = [];
    latencyChart.update();

    // Clear terminal immediately
    document.getElementById("logs").innerHTML = "Waiting for traffic...";

    // Reset backend
    await fetch("/reset", {
        method: "POST"
    });

    // Force a full page reload after backend reset
    window.location.reload(true);

};