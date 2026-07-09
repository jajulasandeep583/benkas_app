<!-- Copyright (c) 2026, Benkas and Contributors — GPL-3.0 -->
<!-- Mobile EOD: file the day's Daily Progress Log from the phone.
     Pick section → add task rows (task + status + % + description) or tick
     No-Work-Today → snap/attach photos → submit. All validation is server-side
     (benkas_erp), so this is identical to the desk. -->
<template>
  <div class="eod">
    <div v-if="loading" class="empty-state" style="padding-top:60px;">
      <ion-spinner name="crescent" color="primary" style="font-size:36px;" />
      <p style="margin-top:10px;">Loading…</p>
    </div>

    <div v-else-if="!meta.available" class="empty-state" style="padding-top:60px;" role="alert">
      <div class="empty-icon" aria-hidden="true">⚠</div>
      <h3>Daily log unavailable</h3>
      <p>benkas_erp is not installed on this site.</p>
    </div>

    <template v-else>
      <!-- Section + date -->
      <div class="eod-card">
        <label class="eod-lbl">Section</label>
        <ion-select v-model="section" interface="action-sheet" placeholder="Pick your section"
                    class="eod-ctrl" @ionChange="onSection">
          <ion-select-option v-for="s in meta.sections" :key="s.name" :value="s.name">
            {{ s.label }}
          </ion-select-option>
        </ion-select>
        <div class="eod-date">Log date: <b>{{ logDate }}</b></div>
      </div>

      <!-- No work today -->
      <div class="eod-card eod-row-between">
        <div>
          <div class="eod-lbl" style="margin:0;">No work today</div>
          <div class="eod-hint">Holiday, full rain day, site closed…</div>
        </div>
        <ion-toggle v-model="noWork" aria-label="No work today" />
      </div>

      <div v-if="noWork" class="eod-card">
        <label class="eod-lbl">Reason (required)</label>
        <ion-textarea v-model="noWorkReason" :rows="2" class="eod-ctrl"
                      placeholder="Why was there no work today?" />
      </div>

      <!-- Task rows -->
      <template v-else>
        <div class="eod-section-title">
          <span>Tasks touched today</span>
          <ion-button size="small" fill="clear" @click="addRow">+ Add task</ion-button>
        </div>

        <div v-if="!section" class="eod-note">Pick a section first.</div>

        <div v-for="(r, i) in rows" :key="i" class="eod-card eod-taskrow">
          <div class="eod-row-between">
            <span class="eod-rownum">Task {{ i + 1 }}</span>
            <ion-button size="small" fill="clear" color="medium" @click="rows.splice(i,1)">Remove</ion-button>
          </div>
          <ion-select v-model="r.task" interface="action-sheet" placeholder="Which task?" class="eod-ctrl">
            <ion-select-option v-for="t in sectionTasks" :key="t.name" :value="t.name">
              {{ t.subject }}
            </ion-select-option>
          </ion-select>
          <div class="eod-grid2">
            <ion-select v-model="r.status" interface="action-sheet" placeholder="Status" class="eod-ctrl">
              <ion-select-option v-for="st in meta.statuses" :key="st.name" :value="st.name">
                {{ st.name }}
              </ion-select-option>
            </ion-select>
            <ion-input v-model.number="r.percent_complete" type="number" min="0" max="100"
                       placeholder="% done" class="eod-ctrl" />
          </div>
          <ion-textarea v-model="r.work_description" :rows="2" class="eod-ctrl"
                        placeholder="What was done — or why it stopped (min 15 chars)" />
          <div class="eod-hint" :class="{ 'eod-warn': descShort(r) }">
            {{ (r.work_description || '').trim().length }}/15 characters
          </div>
        </div>

        <!-- Photos -->
        <div class="eod-section-title">
          <span>Photos <small style="color:#94a3b8;">(at least one for the day)</small></span>
          <ion-button size="small" fill="clear" @click="pickPhoto">+ Add photo</ion-button>
        </div>
        <input ref="fileInput" type="file" accept="image/*" capture="environment"
               style="display:none" @change="onPhoto" />
        <div v-if="photos.length" class="eod-photos">
          <div v-for="(p, i) in photos" :key="i" class="eod-photo">
            <img :src="p.data_uri" alt="site photo" />
            <ion-select v-model="p.activity_task" interface="action-sheet" placeholder="Tag task (optional)"
                        class="eod-ctrl eod-ctrl-sm">
              <ion-select-option :value="null">— no tag —</ion-select-option>
              <ion-select-option v-for="t in sectionTasks" :key="t.name" :value="t.name">
                {{ t.subject }}
              </ion-select-option>
            </ion-select>
            <ion-button size="small" fill="clear" color="medium" @click="photos.splice(i,1)">Remove</ion-button>
          </div>
        </div>
      </template>

      <!-- Submit -->
      <div class="eod-submit">
        <ion-button expand="block" :disabled="submitting || !section" @click="submit">
          <ion-spinner v-if="submitting" name="crescent" style="width:18px;height:18px;margin-right:8px;" />
          {{ submitting ? 'Submitting…' : 'Submit EOD' }}
        </ion-button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, computed, watch } from "vue";
import {
  IonSpinner, IonSelect, IonSelectOption, IonInput, IonTextarea,
  IonToggle, IonButton, toastController,
} from "@ionic/vue";
import { apiFetch } from "@/data/session.js";

const loading = ref(true);
const meta = reactive({ available: false, sections: [], statuses: [], today: "" });
const section = ref("");
const logDate = computed(() => meta.today || new Date().toISOString().slice(0, 10));
const noWork = ref(false);
const noWorkReason = ref("");
const rows = ref([blankRow()]);
const photos = ref([]);
const submitting = ref(false);
const fileInput = ref(null);

function blankRow() {
  return { task: "", status: "", percent_complete: null, work_description: "" };
}

const currentSection = computed(() => meta.sections.find(s => s.name === section.value) || null);
const sectionTasks = computed(() => currentSection.value?.tasks || []);

function descShort(r) {
  return (r.work_description || "").trim().length > 0 && (r.work_description || "").trim().length < 15;
}

onMounted(load);

async function load() {
  loading.value = true;
  try {
    const r = await apiFetch("/api/method/benkas.api.eod.get_eod_meta");
    Object.assign(meta, (await r.json()).message || {});
  } finally {
    loading.value = false;
  }
}

function onSection() {
  // fresh log per section — clear rows/photos so tasks stay in-section
  rows.value = [blankRow()];
  photos.value = [];
}

function addRow() { rows.value.push(blankRow()); }

function pickPhoto() { fileInput.value?.click(); }

function onPhoto(e) {
  const file = e.target.files?.[0];
  e.target.value = "";
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => photos.value.push({ data_uri: reader.result, caption: "", activity_task: null });
  reader.readAsDataURL(file);
}

async function toast(message, color = "danger") {
  const t = await toastController.create({ message, color, duration: 3000, position: "top" });
  await t.present();
}

async function submit() {
  if (!section.value) return toast("Pick a section first.");
  if (noWork.value && !noWorkReason.value.trim()) return toast("Type a reason for the no-work day.");
  if (!noWork.value) {
    const valid = rows.value.filter(r => r.task);
    if (!valid.length) return toast("Add at least one task, or tick No Work Today.");
    if (!photos.value.length) return toast("Add at least one photo for the day.");
  }

  const payload = {
    section: section.value,
    log_date: logDate.value,
    no_work_today: noWork.value ? 1 : 0,
    no_work_reason: noWorkReason.value,
    task_rows: rows.value.filter(r => r.task),
    photos: photos.value,
  };

  submitting.value = true;
  try {
    const r = await apiFetch("/api/method/benkas.api.eod.submit_eod", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload: JSON.stringify(payload) }),
    });
    if (!r.ok) {
      const e = await r.json().catch(() => ({}));
      const msg = (e._server_messages && JSON.parse(e._server_messages)[0]) || e.exception || "Could not submit.";
      let text = msg;
      try { text = JSON.parse(msg).message; } catch (_) { /* plain */ }
      return toast(String(text).replace(/<[^>]*>/g, ""));
    }
    const res = (await r.json()).message;
    await toast(`EOD submitted (${res.name}).`, "success");
    // reset for the next section
    noWork.value = false; noWorkReason.value = "";
    rows.value = [blankRow()]; photos.value = []; section.value = "";
  } catch (err) {
    toast("Network error — try again.");
  } finally {
    submitting.value = false;
  }
}

watch(noWork, (v) => { if (v) { rows.value = [blankRow()]; photos.value = []; } });
</script>

<style scoped>
.eod { padding: 12px 14px 96px; max-width: 640px; margin: 0 auto; }
.eod-card { background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e6e9ef);
  border-radius: 12px; padding: 12px 14px; margin-bottom: 12px; }
.eod-lbl { display: block; font-size: 12px; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: .4px; margin-bottom: 4px; }
.eod-ctrl { --background: #f6f8fb; background: #f6f8fb; border-radius: 8px; padding: 2px 8px;
  border: 1px solid #e6e9ef; margin-top: 2px; }
.eod-ctrl-sm { font-size: 13px; }
.eod-date { font-size: 12px; color: #64748b; margin-top: 8px; }
.eod-row-between { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.eod-hint { font-size: 11px; color: #94a3b8; margin-top: 3px; }
.eod-warn { color: #dc2626; font-weight: 600; }
.eod-section-title { display: flex; align-items: center; justify-content: space-between;
  font-size: 13px; font-weight: 800; color: #16324f; margin: 6px 2px 8px; }
.eod-note { font-size: 13px; color: #94a3b8; padding: 4px 2px 12px; }
.eod-taskrow { border-left: 3px solid #6366f1; }
.eod-rownum { font-size: 12px; font-weight: 700; color: #6366f1; }
.eod-grid2 { display: grid; grid-template-columns: 1fr 100px; gap: 8px; margin-top: 8px; }
.eod-photos { display: flex; flex-direction: column; gap: 10px; }
.eod-photo { display: flex; align-items: center; gap: 10px; background: var(--card-bg,#fff);
  border: 1px solid #e6e9ef; border-radius: 12px; padding: 8px; }
.eod-photo img { width: 64px; height: 64px; object-fit: cover; border-radius: 8px; border: 1px solid #dde; }
.eod-photo .eod-ctrl { flex: 1; }
.eod-submit { position: sticky; bottom: 0; padding: 12px 0 0; background: linear-gradient(transparent, var(--ion-background-color, #fff) 30%); }
</style>
