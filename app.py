import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Flappy 3D", page_icon="🐤", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(160deg, #eefaff 0%, #d8f2ff 48%, #c6e8ff 100%);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stAppViewContainer"] h1 {
        color: #000000;
    }
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🐤 Flappy 3D")
st.caption("Fly through the pipes, keep your wings moving, and beat your high score.")

components.html(
    """
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          * { box-sizing: border-box; }
          body {
            margin: 0;
            overflow: hidden;
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            color: #17324d;
          }
          #game {
            position: relative;
            width: 100%;
            height: 650px;
            overflow: hidden;
            border: 1px solid rgba(78, 144, 185, .2);
            border-radius: 22px;
            background: linear-gradient(#9de5ff, #e4f8ff);
            box-shadow: 0 16px 38px rgba(36, 110, 151, .16);
          }
          canvas { display: block; width: 100%; height: 100%; outline: none; }
          .hud {
            position: absolute;
            z-index: 2;
            top: 18px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            pointer-events: none;
          }
          .badge {
            padding: 9px 15px;
            border: 1px solid rgba(255,255,255,.7);
            border-radius: 14px;
            background: rgba(255,255,255,.68);
            box-shadow: 0 4px 14px rgba(35, 101, 139, .1);
            backdrop-filter: blur(8px);
            font-size: 13px;
            font-weight: 700;
          }
          .score {
            min-width: 88px;
            text-align: center;
            font-size: 24px;
            line-height: 1.1;
            color: #174b67;
          }
          .score small {
            display: block;
            margin-bottom: 4px;
            color: #608399;
            font-size: 10px;
            letter-spacing: .14em;
            text-transform: uppercase;
          }
          .high-score {
            min-width: 102px;
            text-align: center;
            color: #174b67;
            font-size: 20px;
            line-height: 1.1;
          }
          .high-score small {
            display: block;
            margin-bottom: 4px;
            color: #608399;
            font-size: 10px;
            letter-spacing: .14em;
            text-transform: uppercase;
          }
          #overlay {
            position: absolute;
            z-index: 3;
            inset: 0;
            display: grid;
            place-items: center;
            padding: 20px;
            background: rgba(22, 70, 96, .12);
            backdrop-filter: blur(3px);
          }
          #card {
            max-width: 390px;
            padding: 28px 32px;
            border: 1px solid rgba(255,255,255,.85);
            border-radius: 22px;
            background: rgba(255,255,255,.88);
            box-shadow: 0 18px 45px rgba(20, 73, 101, .2);
            text-align: center;
          }
          #card h2 { margin: 0 0 8px; color: #174b67; font-size: 28px; }
          #card p { margin: 0 0 20px; color: #57768a; line-height: 1.55; }
          #play {
            border: 0;
            border-radius: 12px;
            padding: 12px 25px;
            background: #13a978;
            color: white;
            font: inherit;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 5px 0 #0b805a;
            transition: transform .12s, box-shadow .12s, background .12s;
          }
          #play:hover { background: #0d966a; transform: translateY(-1px); }
          #play:active { transform: translateY(3px); box-shadow: 0 2px 0 #0b805a; }
          #hint {
            position: absolute;
            z-index: 2;
            bottom: 16px;
            left: 0;
            right: 0;
            color: rgba(23, 75, 103, .72);
            font-size: 12px;
            font-weight: 700;
            text-align: center;
            pointer-events: none;
          }
          @media (max-width: 600px) {
            #game { height: 560px; border-radius: 16px; }
            #card { padding: 24px 20px; }
            .badge { padding: 8px 11px; font-size: 11px; }
          }
        </style>
      </head>
      <body>
        <div id="game">
          <div class="hud">
            <div class="badge">SPACE · CLICK · TAP to flap</div>
            <div style="display:flex; gap:10px">
              <div class="badge score"><small>Score</small><span id="score">0</span></div>
              <div class="badge high-score"><small>Best</small><span id="high-score">0</span></div>
            </div>
          </div>
          <div id="overlay">
            <div id="card">
              <h2 id="title">Ready to fly?</h2>
              <p id="message">Flap to stay airborne and weave between the 3D pipes. How far can you get?</p>
              <button id="play">Start game</button>
            </div>
          </div>
          <div id="hint">SPACE · CLICK · TAP</div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
          (() => {
            const game = document.getElementById("game");
            const scoreLabel = document.getElementById("score");
            const highScoreLabel = document.getElementById("high-score");
            const overlay = document.getElementById("overlay");
            const title = document.getElementById("title");
            const message = document.getElementById("message");
            const playButton = document.getElementById("play");

            if (!window.THREE) {
              title.textContent = "3D scene unavailable";
              message.textContent = "The game could not load its 3D engine. Check your connection and reload the page.";
              playButton.style.display = "none";
              return;
            }

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x9de5ff);
            scene.fog = new THREE.Fog(0x9de5ff, 17, 36);
            const camera = new THREE.OrthographicCamera(-8, 8, 5, -5, 0.1, 100);
            camera.position.set(0, 0, 18);
            camera.lookAt(0, 0, 0);

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
            renderer.outputEncoding = THREE.sRGBEncoding;
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            game.insertBefore(renderer.domElement, game.firstChild);
            renderer.domElement.setAttribute("aria-label", "Flappy 3D game");
            renderer.domElement.tabIndex = 0;

            scene.add(new THREE.HemisphereLight(0xeafaff, 0x5b8e68, 1.7));
            const sunlight = new THREE.DirectionalLight(0xffffff, 2.1);
            sunlight.position.set(-4, 9, 11);
            sunlight.castShadow = true;
            sunlight.shadow.mapSize.set(1024, 1024);
            scene.add(sunlight);

            const skyMaterial = new THREE.MeshStandardMaterial({ color: 0x9de5ff, roughness: 1 });
            const sky = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), skyMaterial);
            sky.position.z = -18;
            scene.add(sky);

            const ground = new THREE.Mesh(
              new THREE.BoxGeometry(200, 1.2, 8),
              new THREE.MeshStandardMaterial({ color: 0x82d484, roughness: .9 })
            );
            ground.position.set(0, -5.25, 0);
            ground.receiveShadow = true;
            scene.add(ground);
            const groundLine = new THREE.Mesh(
              new THREE.BoxGeometry(200, .16, 8.1),
              new THREE.MeshStandardMaterial({ color: 0x4ab975, roughness: .8 })
            );
            groundLine.position.set(0, -4.63, .04);
            scene.add(groundLine);

            const cloudMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 1 });
            const clouds = [];
            for (let i = 0; i < 6; i++) {
              const cloud = new THREE.Group();
              for (let j = 0; j < 3; j++) {
                const puff = new THREE.Mesh(new THREE.SphereGeometry(.38 + (j === 1 ? .16 : 0), 16, 12), cloudMaterial);
                puff.position.set((j - 1) * .42, j === 1 ? .12 : 0, 0);
                cloud.add(puff);
              }
              cloud.position.set(-9 + i * 4.4, 2.5 + (i % 3) * .65, -5);
              cloud.scale.setScalar(.8 + (i % 2) * .2);
              scene.add(cloud);
              clouds.push(cloud);
            }

            const bird = new THREE.Group();
            const bodyMaterial = new THREE.MeshStandardMaterial({ color: 0xffc83d, roughness: .42 });
            const body = new THREE.Mesh(new THREE.SphereGeometry(.38, 28, 20), bodyMaterial);
            body.scale.set(1.12, .9, .9);
            body.castShadow = true;
            bird.add(body);
            const wing = new THREE.Mesh(
              new THREE.SphereGeometry(.22, 20, 14),
              new THREE.MeshStandardMaterial({ color: 0xf29b2e, roughness: .5 })
            );
            wing.scale.set(.75, .48, .45);
            wing.position.set(-.08, -.12, .31);
            wing.castShadow = true;
            bird.add(wing);
            const eyeWhite = new THREE.Mesh(
              new THREE.SphereGeometry(.115, 16, 12),
              new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: .25 })
            );
            eyeWhite.position.set(.2, .13, .31);
            bird.add(eyeWhite);
            const pupil = new THREE.Mesh(
              new THREE.SphereGeometry(.057, 14, 10),
              new THREE.MeshStandardMaterial({ color: 0x17324d, roughness: .3 })
            );
            pupil.position.set(.235, .13, .405);
            bird.add(pupil);
            const beak = new THREE.Mesh(
              new THREE.ConeGeometry(.16, .34, 5),
              new THREE.MeshStandardMaterial({ color: 0xff7139, roughness: .45 })
            );
            beak.rotation.z = -Math.PI / 2;
            beak.position.set(.48, -.02, .04);
            bird.add(beak);
            bird.position.set(-2.4, 0, 1);
            scene.add(bird);

            const pipeMaterial = new THREE.MeshStandardMaterial({ color: 0x20ae69, roughness: .52 });
            const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x39cf7d, roughness: .42 });
            const pipeRadius = .48;
            const worldTop = 4.35;
            const worldBottom = -4.35;
            const gapSize = 2.75;
            const pipes = [];
            let running = false;
            let velocity = 0;
            let elapsed = 0;
            let score = 0;
            let highScore = 0;
            try {
              highScore = Number(window.localStorage.getItem("flappy3d-high-score")) || 0;
            } catch (error) {
              console.warn("Could not load the saved high score.", error);
            }
            highScoreLabel.textContent = String(highScore);
            let lastTime = performance.now();
            let spawnTimer = 0;

            function addPipePart(group, y, height, material, radius) {
              if (height <= 0) return;
              const mesh = new THREE.Mesh(
                new THREE.CylinderGeometry(radius, radius, height, 20),
                material
              );
              mesh.position.set(0, y, 0);
              mesh.castShadow = true;
              mesh.receiveShadow = true;
              group.add(mesh);
            }

            function createPipe(x) {
              const gapCenter = THREE.MathUtils.randFloat(-.9, 1.1);
              const gapTop = gapCenter + gapSize / 2;
              const gapBottom = gapCenter - gapSize / 2;
              const group = new THREE.Group();
              group.position.set(x, 0, 0);
              addPipePart(group, (worldTop + gapTop) / 2, worldTop - gapTop, pipeMaterial, pipeRadius);
              addPipePart(group, gapTop - .12, .24, rimMaterial, pipeRadius + .13);
              addPipePart(group, (worldBottom + gapBottom) / 2, gapBottom - worldBottom, pipeMaterial, pipeRadius);
              addPipePart(group, gapBottom + .12, .24, rimMaterial, pipeRadius + .13);
              group.userData = { gapTop, gapBottom, scored: false };
              scene.add(group);
              pipes.push(group);
            }

            function showOverlay(isGameOver) {
              overlay.style.display = "grid";
              title.textContent = isGameOver ? "Nice flight!" : "Ready to fly?";
              message.textContent = isGameOver
                ? `You scored ${score}. Give it another go and beat your best!`
                : "Flap to stay airborne and weave between the 3D pipes. How far can you get?";
              playButton.textContent = isGameOver ? "Play again" : "Start game";
            }

            function startGame() {
              for (const pipe of pipes) scene.remove(pipe);
              pipes.length = 0;
              score = 0;
              scoreLabel.textContent = "0";
              elapsed = 0;
              spawnTimer = 0;
              velocity = 0;
              bird.position.y = 0;
              bird.rotation.z = 0;
              running = true;
              overlay.style.display = "none";
              flap();
              renderer.domElement.focus();
            }

            function endGame() {
              running = false;
              if (score > highScore) {
                highScore = score;
                highScoreLabel.textContent = String(highScore);
                try {
                  window.localStorage.setItem("flappy3d-high-score", String(highScore));
                } catch (error) {
                  console.warn("Could not save the high score.", error);
                }
              }
              showOverlay(true);
            }

            function flap() {
              if (!running) return;
              velocity = 6.4;
            }

            function resize() {
              const width = game.clientWidth;
              const height = game.clientHeight;
              const aspect = width / height;
              camera.left = -5 * aspect;
              camera.right = 5 * aspect;
              camera.top = 5;
              camera.bottom = -5;
              camera.updateProjectionMatrix();
              renderer.setSize(width, height, false);
            }

            playButton.addEventListener("click", startGame);
            game.addEventListener("pointerdown", (event) => {
              if (event.target === playButton || !running) return;
              flap();
            });
            window.addEventListener("keydown", (event) => {
              if (event.code === "Space" || event.code === "ArrowUp") {
                event.preventDefault();
                flap();
              }
            });
            window.addEventListener("resize", resize);
            new ResizeObserver(resize).observe(game);
            resize();

            function animate(now) {
              requestAnimationFrame(animate);
              const dt = Math.min((now - lastTime) / 1000, .04);
              lastTime = now;
              elapsed += dt;
              clouds.forEach((cloud, index) => {
                cloud.position.x -= dt * (.12 + index * .012);
                if (cloud.position.x < -11) cloud.position.x = 11;
              });

              if (running) {
                velocity -= 15.5 * dt;
                bird.position.y += velocity * dt;
                bird.rotation.z = THREE.MathUtils.clamp(velocity * .075, -.65, .55);
                wing.rotation.z = Math.sin(elapsed * 19) * .35;
                spawnTimer += dt;
                if (spawnTimer >= 2.05) {
                  spawnTimer = 0;
                  createPipe(camera.right + 1.4);
                }
                const speed = 3.15 + Math.min(score * .055, 1.4);
                for (let i = pipes.length - 1; i >= 0; i--) {
                  const pipe = pipes[i];
                  pipe.position.x -= speed * dt;
                  const horizontalDistance = Math.abs(pipe.position.x - bird.position.x);
                  if (horizontalDistance < .78 &&
                      (bird.position.y + .29 > pipe.userData.gapTop ||
                       bird.position.y - .29 < pipe.userData.gapBottom)) {
                    endGame();
                    break;
                  }
                  if (!pipe.userData.scored && pipe.position.x < bird.position.x) {
                    pipe.userData.scored = true;
                    score += 1;
                    scoreLabel.textContent = String(score);
                  }
                  if (pipe.position.x < camera.left - 1.5) {
                    scene.remove(pipe);
                    pipes.splice(i, 1);
                  }
                }
                if (bird.position.y < -4.05 || bird.position.y > 4.65) endGame();
              } else {
                bird.position.y = Math.sin(elapsed * 2.4) * .12;
                bird.rotation.z = Math.sin(elapsed * 2.4) * .04;
                wing.rotation.z = Math.sin(elapsed * 5) * .15;
              }
              renderer.render(scene, camera);
            }
            requestAnimationFrame(animate);
          })();
        </script>
      </body>
    </html>
    """,
    height=670,
    scrolling=False,
)

st.caption("Tip: press **Space** or **↑**, or click/tap the game to flap.")
