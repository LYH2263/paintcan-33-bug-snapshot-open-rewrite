<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getJSON } from '../api'
const items = ref([])
const qid = ref(null)
const router = useRouter()
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
const open = () => { if (qid.value != null) router.push(`/history/${qid.value}`) }
</script>
<template><div class="page"><h1>估算记录</h1>
<form @submit.prevent="open">
  <label>按编号打开 <input v-model.number="qid" type="number" min="1" /></label>
  <button type="submit">打开</button>
</form>
<table><tr v-for="h in items" :key="h.id">
  <td><router-link :to="`/history/${h.id}`">#{{ h.id }}</router-link></td>
  <td>{{ h.created_at }}</td>
  <td v-if="h.result && h.result.liters != null">{{ h.result.liters }} 升</td>
</tr></table></div></template>
