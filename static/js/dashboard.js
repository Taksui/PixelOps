// ======================================================
// PixelOps Dashboard v2
// ======================================================

// ------------------------------------------------------
// Globals
// ------------------------------------------------------

const MAX_POINTS = 30;

let editingChaos = false;

let trafficLoop = null;

let achievements = new Set();

let replayMode = false;

let replayFrames = [];

let replayIndex = 0;

let replayTimer = null;

let replayDelay = 500;



// ------------------------------------------------------
// Helper
// ------------------------------------------------------

function $(id){

    return document.getElementById(id);

}

// ------------------------------------------------------
// Animated Counter
// ------------------------------------------------------

function animateValue(id,newValue){

    const element=$(id);

    if(!element) return;

    const oldValue=parseInt(
        element.innerText.replace(/\D/g,"")
    )||0;

    if(oldValue===newValue){

        element.innerText=newValue;

        return;

    }

    const duration=250;

    const fps=60;

    const totalFrames=duration/(1000/fps);

    let frame=0;

    const diff=newValue-oldValue;

    clearInterval(element.timer);

    element.timer=setInterval(()=>{

        frame++;

        const value=Math.round(

            oldValue+

            diff*(frame/totalFrames)

        );

        element.innerText=value;

        if(frame>=totalFrames){

            clearInterval(

                element.timer

            );

            element.innerText=newValue;

        }

    },1000/fps);

}

// ------------------------------------------------------
// Push Value Into Chart
// ------------------------------------------------------

function pushChart(chart,value){

    chart.data.labels.push("");

    chart.data.datasets[0].data.push(value);

    if(chart.data.labels.length>MAX_POINTS){

        chart.data.labels.shift();

        chart.data.datasets[0].data.shift();

    }

    chart.update();

}

// ------------------------------------------------------
// Toast
// ------------------------------------------------------

function toast(message,type="success"){

    const container=$("toastContainer");

    if(!container) return;

    const div=document.createElement("div");

    div.className=`toast ${type}`;

    div.innerText=message;

    container.appendChild(div);

    setTimeout(()=>{

        div.style.animation=

            "toastOut .3s forwards";

        setTimeout(()=>{

            div.remove();

        },300);

    },2400);

}

function stopReplay() {

    replayMode = false;

}
// ------------------------------------------------------
// Charts
// ------------------------------------------------------

const requestChart=new Chart(

    $("requestChart"),

    {

        type:"line",

        data:{

            labels:[],

            datasets:[{

                label:"Requests/sec",

                data:[],

                borderColor:"#37f5d4",

                borderWidth:3,

                tension:.35,

                fill:false

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

            animation:false,

            plugins:{

                legend:{

                    labels:{

                        color:"#ffffff"

                    }

                }

            },

            scales:{

                x:{

                    ticks:{

                        color:"#ffffff"

                    }

                },

                y:{

                    ticks:{

                        color:"#ffffff"

                    }

                }

            }

        }

    }

);

const latencyChart=new Chart(

    $("latencyChart"),

    {

        type:"line",

        data:{

            labels:[],

            datasets:[{

                label:"Latency",

                data:[],

                borderColor:"#ffd84a",

                borderWidth:3,

                tension:.35,

                fill:false

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

            animation:false,

            plugins:{

                legend:{

                    labels:{

                        color:"#ffffff"

                    }

                }

            },

            scales:{

                x:{

                    ticks:{

                        color:"#ffffff"

                    }

                },

                y:{

                    ticks:{

                        color:"#ffffff"

                    }

                }

            }

        }

    }

);

const statusChart=new Chart(

    $("statusChart"),

    {

        type:"doughnut",

        data:{

            labels:[

                "200",

                "429",

                "500"

            ],

            datasets:[{

                data:[0,0,0],

                backgroundColor:[

                    "#45ff7a",

                    "#ffd84a",

                    "#ff4040"

                ],

                borderWidth:2,

                borderColor:"#2b2340"

            }]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

            animation:false,

            plugins:{

                legend:{

                    position:"bottom",

                    labels:{

                        color:"#ffffff"

                    }

                }

            }

        }

    }

);

// ------------------------------------------------------
// Chaos Editing Detection
// ------------------------------------------------------

[

    "failureRate",

    "minLatency",

    "maxLatency",

    "retryAttempts",

    "rateLimit"

].forEach(id=>{

    const el=$(id);

    if(!el) return;

    el.addEventListener(

        "focus",

        ()=>editingChaos=true

    );

    el.addEventListener(

        "blur",

        ()=>editingChaos=false

    );

});
// ======================================================
// Dashboard Refresh
// ======================================================

async function updateDashboard(){

    try{

        const res=await fetch("/dashboard-data");

        const data=await res.json();

        const m=data.metrics;

        // --------------------------------------------------
        // Animated Metric Cards
        // --------------------------------------------------

        animateValue(

            "request-count",

            m.total_requests

        );

        animateValue(

            "failure-count",

            m.failures

        );

        $("success-rate").innerText=

            m.success_rate+"%";

        $("latency").innerText=

            Math.round(

                m.average_latency_ms

            )+" ms";

        // --------------------------------------------------
        // Boss
        // --------------------------------------------------

        $("boss-hp").style.width=

            m.health+"%";

        const dragon=$("dragon");

        const boss=$("boss-status");

        dragon.className="dragon";

        if(m.health>80){

            dragon.innerText="🐉";

            boss.innerText="Sleeping";

        }

        else if(m.health>60){

            dragon.innerText="🐲";

            dragon.classList.add("rage");

            boss.innerText="Alert";

        }

        else if(m.health>30){

            dragon.innerText="🔥🐲";

            dragon.classList.add("berserk");

            boss.innerText="BERSERK";

        }

        else if(m.health>0){

            dragon.innerText="👹";

            dragon.classList.add("berserk");

            boss.innerText="FINAL FORM";

        }

        else{

            dragon.innerText="💀";

            dragon.classList.add("dead");

            boss.innerText="DEFEATED";

        }

        // --------------------------------------------------
        // Status Badge
        // --------------------------------------------------

        const badge=

            document.querySelector(".status");

        badge.innerText=

            m.system_status;

        switch(m.system_status){

            case "ONLINE":

                badge.style.background="#45ff7a";

                badge.style.color="#000";

                break;

            case "DEGRADED":

                badge.style.background="#ffd84a";

                badge.style.color="#000";

                break;

            default:

                badge.style.background="#ff4040";

                badge.style.color="#fff";

        }

        // --------------------------------------------------
        // Charts
        // --------------------------------------------------

        pushChart(

            requestChart,

            m.requests_per_second

        );

        pushChart(

            latencyChart,

            m.average_latency_ms

        );

        const codes=

            m.status_codes||{};

        statusChart.data.datasets[0].data=[

            codes["200"]||0,

            codes["429"]||0,

            codes["500"]||0

        ];

        statusChart.update();

        // --------------------------------------------------
        // Terminal Logs
        // --------------------------------------------------

        const logs=$("logs");

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

                    ${log.latency_ms} ms

                    </p>

                `;

            });

        logs.scrollTop=

            logs.scrollHeight;

        // --------------------------------------------------
        // Recent Requests Table
        // --------------------------------------------------

        const table=

            $("requestTableBody");

        if(table){

            table.innerHTML="";

            data.recent_logs

                .slice()

                .reverse()

                .forEach(log=>{

                    table.innerHTML+=`

                    <tr>

                        <td>

                            ${log.timestamp.slice(11,19)}

                        </td>

                        <td>

                            ${log.endpoint}

                        </td>

                        <td>

                            ${log.status}

                        </td>

                        <td>

                            ${log.latency_ms} ms

                        </td>

                        <td>

                            ${log.attempts}

                        </td>

                    </tr>

                    `;

                });

        }

        // --------------------------------------------------
        // Chaos Controls
        // --------------------------------------------------

        if(!editingChaos){

            const chaos=

                await fetch("/chaos/current");

            const cfg=

                await chaos.json();

            $("failureRate").value=

                cfg.failure_rate;

            $("failureValue").innerText=

                Math.round(

                    cfg.failure_rate*100

                )+"%";

            $("minLatency").value=

                cfg.min_latency;

            $("maxLatency").value=

                cfg.max_latency;

            $("retryAttempts").value=

                cfg.retry_attempts;

            $("rateLimit").value=

                cfg.rate_limit;

        }

    }

    catch(err){

        console.error(

            "Dashboard Error",

            err

        );

    }

}
// ======================================================
// Manual Requests
// ======================================================

async function sendRequests(count){

    const jobs=[];

    for(

        let i=0;

        i<count;

        i++

    ){

        jobs.push(

            fetch("/data")

        );

    }

    await Promise.allSettled(jobs);

}

$("sendOne").onclick=async()=>{

    toast(

        "Sent 1 Request"

    );

    await sendRequests(1);

};

$("sendTen").onclick=async()=>{

    toast(

        "Sent 10 Requests"

    );

    await sendRequests(10);

};

$("sendHundred").onclick=async()=>{

    toast(

        "Sent 100 Requests"

    );

    await sendRequests(100);

};

$("chaosMode").onclick=async()=>{

    toast(

        "CHAOS MODE",

        "warning"

    );

    await sendRequests(500);

};

$("screenshotBtn").onclick=()=>{

    captureDashboard();

};

$("exportReport").onclick=()=>{

    exportReport();

};

$("replayBtn").onclick = replaySimulation;

$("replaySpeed").addEventListener("change", function () {

    replayDelay = Number(this.value);

});

$("stopReplay").onclick = stopReplay;

// ======================================================
// Traffic Generator
// ======================================================

const slider=$("trafficRate");

const trafficValue=$("trafficValue");

slider.oninput=()=>{

    trafficValue.innerText=

        slider.value+

        " req/sec";

};

$("startTraffic").onclick=()=>{

    if(

        trafficLoop

    )

        return;

    toast(

        "Traffic Started"

    );

    $("trafficStatus").innerText=

        "🟢 Running";

    trafficLoop=setInterval(

        ()=>{

            sendRequests(

                Number(

                    slider.value

                )

            );

        },

        1000

    );

};

$("stopTraffic").onclick=()=>{

    if(

        trafficLoop

    ){

        clearInterval(

            trafficLoop

        );

        trafficLoop=null;

    }

    $("trafficStatus").innerText=

        "🔴 Idle";

    toast(

        "Traffic Stopped",

        "warning"

    );

};

// ======================================================
// Chaos Controls
// ======================================================

$("failureRate").oninput=()=>{

    $("failureValue").innerText=

        Math.round(

            $("failureRate").value*100

        )+"%";

};

$("applyChaos").onclick=async()=>{

    const payload={

        failure_rate:Number(

            $("failureRate").value

        ),

        min_latency:Number(

            $("minLatency").value

        ),

        max_latency:Number(

            $("maxLatency").value

        ),

        retry_attempts:Number(

            $("retryAttempts").value

        ),

        rate_limit:Number(

            $("rateLimit").value

        )

    };

    await fetch(

        "/chaos/update",

        {

            method:"POST",

            headers:{

                "Content-Type":

                "application/json"

            },

            body:JSON.stringify(

                payload

            )

        }

    );

    toast(

        "Chaos Updated"

    );

    updateDashboard();

};

// ======================================================
// Reset
// ======================================================

$("resetSim").onclick=async()=>{

    if(

        trafficLoop

    ){

        clearInterval(

            trafficLoop

        );

        trafficLoop=null;

    }

    $("trafficStatus").innerText=

        "🔴 Idle";

    requestChart.data.labels=[];

    requestChart.data.datasets[0].data=[];

    requestChart.update();

    latencyChart.data.labels=[];

    latencyChart.data.datasets[0].data=[];

    latencyChart.update();

    statusChart.data.datasets[0].data=[

        0,

        0,

        0

    ];

    statusChart.update();

    $("logs").innerHTML=

        "Waiting for traffic...";

    const table=$(

        "requestTableBody"

    );

    if(table)

        table.innerHTML="";

    await fetch(

        "/reset",

        {

            method:"POST"

        }

    );

    toast(

        "Simulation Reset"

    );

    setTimeout(

        ()=>{

            updateDashboard();

        },

        300

    );

};
// ======================================================
// Achievements
// ======================================================

function unlockAchievement(title){

    if(achievements.has(title))
        return;

    achievements.add(title);

    const popup=document.createElement("div");

    popup.className="achievement";

    popup.innerHTML=`
        <h3>🏆 Achievement Unlocked!</h3>
        <p>${title}</p>
    `;

    document.body.appendChild(popup);

    setTimeout(()=>{

        popup.remove();

    },3000);

}

// ======================================================
// Achievement Checker
// ======================================================

function checkAchievements(metrics){

    if(metrics.total_requests>=1)
        unlockAchievement("First Request");

    if(metrics.total_requests>=100)
        unlockAchievement("100 Requests");

    if(metrics.total_requests>=1000)
        unlockAchievement("1000 Requests");

    if(metrics.success_rate===100 &&
       metrics.total_requests>=25)
        unlockAchievement("Perfect Run");

    if(metrics.failures>=100)
        unlockAchievement("Chaos Master");

    if(metrics.health<=0)
        unlockAchievement("Dragon Slayer");

}

// ======================================================
// Keyboard Shortcuts
// ======================================================

document.addEventListener(

    "keydown",

    e=>{

        // Don't trigger shortcuts while typing
        if(
            document.activeElement.tagName==="INPUT"
        ) return;

        switch(e.key.toLowerCase()){

            case "1":

                sendRequests(1);

                break;

            case "2":

                sendRequests(10);

                break;

            case "3":

                sendRequests(100);

                break;

            case "c":

                sendRequests(500);

                break;

            case "r":

                $("resetSim").click();

                break;

            case "s":

                $("startTraffic").click();

                break;

            case "x":

                $("stopTraffic").click();

                break;

        }

    }

);

// ======================================================
// Future Hooks
// ======================================================

// Export PDF
async function exportReport(){

    toast(

        "Generating Report..."

    );

    window.location=

        "/export/report";

}

// Screenshot
async function captureDashboard(){

    toast("Capturing Dashboard...");

    const dashboard=document.querySelector(".dashboard");

    const canvas=await html2canvas(

        dashboard,

        {

            backgroundColor:"#221b36",

            scale:2,

            useCORS:true

        }

    );

    const link=document.createElement("a");

    const now=new Date();

    const timestamp=

        now.toISOString()

        .replace(/:/g,"-")

        .slice(0,19);

    link.download=

        `pixelops-${timestamp}.png`;

    link.href=

        canvas.toDataURL("image/png");

    link.click();

    toast("Screenshot Saved!");

}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Replay
async function replaySimulation() {

    replayMode = true;

    replayIndex = 0;

    const response = await fetch("/replay/start");
    const data = await response.json();

    replayFrames = data.frames;

    if (!replayFrames.length) {

        alert("No replay data available.");

        replayMode = false;

        return;
    }

    while (
        replayMode &&
        replayIndex < replayFrames.length
    ) {

        const frame = replayFrames[replayIndex];

        updateReplayDashboard(frame);

        replayIndex++;

        await sleep(replayDelay);

    }

    replayMode = false;

}

function updateReplayDashboard(frame) {

    // Metric cards
    document.getElementById("request-count").innerText =
        frame.total_requests;

    document.getElementById("success-rate").innerText =
        frame.success_rate + "%";

    document.getElementById("failure-count").innerText =
        frame.failures;

    document.getElementById("latency").innerText =
        frame.average_latency + " ms";


    // Boss HP
    document.getElementById("boss-hp").style.width =
        frame.health + "%";

    if (frame.health > 70)
        document.getElementById("boss-status").innerText = "Sleeping";

    else if (frame.health > 40)
        document.getElementById("boss-status").innerText = "Angry";

    else
        document.getElementById("boss-status").innerText = "BERSERK";


    // Logs
    document.getElementById("logs").innerHTML =
        `<div>${frame.log.status} | ${frame.log.endpoint} | ${frame.log.latency_ms} ms</div>`;


    // Recent Request Table
    document.getElementById("requestTableBody").innerHTML =
        `
        <tr>
            <td>${frame.log.timestamp.split("T")[1].split(".")[0]}</td>
            <td>${frame.log.endpoint}</td>
            <td>${frame.log.status}</td>
            <td>${frame.log.latency_ms}</td>
            <td>${frame.log.attempts}</td>
        </tr>
        `;
}

// ======================================================
// Dashboard Polling
// ======================================================

async function dashboardLoop(){

    await updateDashboard();

    try{

        const res=await fetch("/metrics");

        const metrics=await res.json();

        checkAchievements(metrics);

    }

    catch(err){

        console.error(err);

    }

}

setInterval(

    dashboardLoop,

    1000

);

// ======================================================
// Startup
// ======================================================

window.onload=()=>{

    // Slider label

    trafficValue.innerText=

        slider.value+

        " req/sec";

    // Initial dashboard

    dashboardLoop();

    toast(

        "PixelOps Ready"

    );

};

console.log("Reached sidebar code");

// ============================================
// Sidebar Navigation
// ============================================

function scrollToSection(id){

    document.getElementById(id).scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}

$("navDashboard").onclick = () => scrollToSection("dashboard");

$("navMetrics").onclick = () => scrollToSection("metrics");

$("navChaos").onclick = () => scrollToSection("chaos");

$("navCharts").onclick = () => scrollToSection("charts");

$("navLogs").onclick = () => scrollToSection("logsSection");

$("navSettings").onclick = function(){

    alert(

`PixelOps v1.0

Built by Dave Aashisth

Tech Stack

• FastAPI
• Docker
• Chart.js
• GitHub Actions
• Render

Production-inspired Chaos Engineering Simulator`

    );

};
