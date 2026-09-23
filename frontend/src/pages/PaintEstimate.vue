<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { postJSON } from '../api'
const router = useRouter()
const room_id = ref(1)
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''; out.value = null
  try {
    const r = await postJSON('/api/estimate', { room_id: room_id.value, persist: true })
    out.value = r
    if (r.run_id != null) router.push(`/history/${r.run_id}`)
  } catch (e) { err.value = '写入失败：房间不存在或参数有误' }
}
</script>
<template><div class="page"><h1>估漆工作台</h1>
<label>房间ID <input v-model.number="room_id" /></label>
<button @click="run">估算并写入</button>
<p v-if="err" class="error">{{ err }}</p>
<p v-if="out">净 {{ out.net_m2 }} m² · {{ out.liters }} 升 · {{ out.coats }} 遍 · 编号 #{{ out.run_id }}</p></div></template>
