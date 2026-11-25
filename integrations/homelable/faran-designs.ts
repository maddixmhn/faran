import type { Edge, Node } from '@xyflow/react'
import type { EdgeData, NodeData, NodeType } from '@/types'
import { universityMaps } from './universityDesigns'

type Service = [id: string, label: string, type: NodeType, x: number, y: number, notes: string]
type Link = [source: string, target: string, label: string]

function canvas(id: string, name: string, services: Service[], links: Link[]) {
  const nodes: Node<NodeData>[] = services.map(([id, label, type, x, y, notes]) => ({
    id, type, position: { x, y },
    data: { label, type, notes, status: 'unknown', services: [], left_handles: 1, right_handles: 1 },
  }))
  const positions = new Map(nodes.map(node => [node.id, node.position]))
  const edges: Edge<EdgeData>[] = links.map(([source, target, label]) => {
    const from = positions.get(source)!
    const to = positions.get(target)!
    const horizontal = from.y === to.y
    return {
      id: `${source}-${target}`, source, target,
      sourceHandle: horizontal ? (from.x < to.x ? 'right' : 'left') : 'bottom',
      targetHandle: horizontal ? (from.x < to.x ? 'left' : 'right') : 'top',
      type: 'virtual', data: { type: 'virtual', label },
    }
  })
  return { id, name, nodes, edges, theme_id: 'dark' as const }
}

export const faranDesigns = [
  canvas('faran-infrastructure', 'زیرساخت فاران', [
    ['faran-web', 'وب فاران', 'computer', 90, 30, 'نمای دانشگاه و دسترسی به منابع سمینار.'],
    ['evaluator-web', 'وب ارزیاب', 'computer', 410, 30, 'نمای ارزیابی و تحلیل شواهد گردش‌کار.'],
    ['summary', 'خلاصهٔ اجرا', 'docker_container', 250, 170, 'دادهٔ پالایش‌شدهٔ اجرا را در محیط محلی به داشبوردها می‌رساند.'],
    ['paperclip', 'Paperclip', 'ai_server', 25, 320, 'مدیریت کار و ثبت شناسهٔ وظیفه در محیط آزمایشی.'],
    ['n8n', 'n8n', 'docker_container', 250, 320, 'اجرا و ثبت تاریخچهٔ گردش‌کار.'],
    ['moodle', 'Moodle', 'server', 500, 320, 'ثبت و بازخوانی عضویت آموزشی در درس.'],
    ['postgres', 'PostgreSQL', 'nas', 150, 470, 'پایگاه دادهٔ اجرای n8n در حالت صف.'],
    ['redis', 'Redis', 'nas', 365, 470, 'صف کار برای اجرای n8n.'],
  ], [
    ['faran-web', 'summary', 'خلاصهٔ محلی'], ['evaluator-web', 'summary', 'شواهد پالایش‌شده'],
    ['summary', 'paperclip', 'رد وظیفه'], ['summary', 'n8n', 'رد اجرا'],
    ['paperclip', 'n8n', 'تحویل کار'], ['n8n', 'moodle', 'ثبت و بازخوانی'],
    ['n8n', 'postgres', 'تاریخچه'], ['n8n', 'redis', 'صف اجرا'],
  ]),
  canvas('evaluator-evidence', 'مسیر شواهد ارزیاب', [
    ['paperclip', 'وظیفهٔ Paperclip', 'ai_server', 35, 30, 'شناسهٔ وظیفه و زمان تحویل.'],
    ['n8n', 'اجرای n8n', 'docker_container', 255, 30, 'زمان شروع، پایان و شناسهٔ اجرا.'],
    ['moodle', 'رسید Moodle', 'server', 475, 30, 'بازخوانی عضویت برای تأیید نتیجه.'],
    ['trace', 'شواهد هم‌شناسه', 'nas', 255, 190, 'رویدادها با شناسهٔ مشترک برای تحلیل آماده می‌شوند.'],
    ['queue', 'زمان صف و خدمت', 'generic', 35, 345, 'مقایسهٔ زمان انتظار و زمان اجرای هر مرحله.'],
    ['rules', 'صحت ثبت‌نام', 'generic', 475, 345, 'بررسی نتیجه با قواعد و رسید عضویت.'],
    ['report', 'گزارش ارزیاب', 'computer', 255, 505, 'خلاصهٔ یافته‌ها، معیارها و منبع هر نتیجه.'],
  ], [
    ['paperclip', 'trace', 'وظیفه'], ['n8n', 'trace', 'رسید اجرا'], ['moodle', 'trace', 'شاهد نتیجه'],
    ['trace', 'queue', 'زمان‌ها'], ['trace', 'rules', 'رخدادها'],
    ['queue', 'report', 'شاخص‌ها'], ['rules', 'report', 'یافته‌ها'],
  ]),
]

export const universityDesigns = universityMaps.map(({ id, name, entries, links }) => ({
  id, name, getCanvas: () => canvas(id, name, entries, links),
}))
