<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
const route = useRoute()
const item = ref(null)
const err = ref('')
const load = async (id) => {
  item.value = null; err.value = ''
  try { item.value = await getJSON(`/api/history/${id}`) }
  catch (e) { err.value = `打开失败：编号 ${id} 不存在` }
}
onMounted(() => load(route.params.id))
watch(() => route.params.id, (id) => load(id))
</script>
<template><div class="page">
  <h1>估算详情</h1>
  <p v-if="err" class="error">{{ err }}</p>
  <table v-if="item">
    <tr><td>编号</td><td>#{{ item.id }}</td></tr>
    <tr><td>房间</td><td>{{ item.room_id }}</td></tr>
    <tr><td>写入时间</td><td>{{ item.created_at }}</td></tr>
    <tr><td>净面积</td><td>{{ item.result.net_m2 }} m²</td></tr>
    <tr><td>开洞扣除</td><td>{{ item.result.openings_m2 }} m²</td></tr>
    <tr><td>用漆量</td><td>{{ item.result.liters }} 升</td></tr>
    <tr><td>涂布率</td><td>{{ item.result.coverage }} m²/升</td></tr>
    <tr><td>遍数</td><td>{{ item.result.coats }} 遍</td></tr>
  </table>
  <p><router-link to="/history">返回记录列表</router-link></p>
</div></template>
