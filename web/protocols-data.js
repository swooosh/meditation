// Protocol data structure
const PROTOCOLS = {
    ATTN: {
        name: "Attention Training",
        description: "Develop focused, sustained, and distributed attention capacity",
        protocols: [
            { id: "FSP-01", title: "Focused Sustained Practice", duration: "31m", goal: "Develop stable sustained attention" },
            { id: "FSP-02", title: "Distributed Attention", duration: "25m", goal: "Train panoramic awareness" },
            { id: "FSP-03", title: "Rapid Context Switching", duration: "15m", goal: "Cognitive flexibility training" }
        ]
    },
    ARC: {
        name: "Breath-Driven Intensity",
        description: "Somatic activation through rhythmic breathwork",
        protocols: [
            { id: "ARC-1TB", title: "Tribal Breathwork", duration: "60m", goal: "Access non-ordinary states" },
            { id: "ARC-2", title: "Gentle Activation", duration: "45m", goal: "Beginner breathwork capacity" },
            { id: "ARC-3", title: "Peak Intensity", duration: "30m", goal: "Maximum sustainable intensity" }
        ]
    },
    PERF: {
        name: "Performance State",
        description: "Optimize arousal for high-stakes performance",
        protocols: [
            { id: "PERF-01", title: "Pre-Mission Focus", duration: "12m", goal: "Calm-alert readiness state" },
            { id: "PERF-02", title: "Post-Performance Recovery", duration: "15m", goal: "Rapid parasympathetic return" },
            { id: "PERF-03", title: "Micro-Dose Focus", duration: "5m", goal: "Immediate cognitive sharpness" }
        ]
    },
    RECON: {
        name: "Emotional Processing",
        description: "Safe exploration and integration of emotional material",
        protocols: [
            { id: "RECON-01", title: "Memory Reconsolidation", duration: "25m", goal: "Update emotional memories" },
            { id: "RECON-02", title: "Grief Container", duration: "35m", goal: "Process loss and difficult emotion safely" },
            { id: "RECON-03", title: "Shadow Integration", duration: "40m", goal: "Integrate disowned parts" }
        ]
    },
    SLEEP: {
        name: "Sleep Architecture",
        description: "Navigate threshold states and deep rest",
        protocols: [
            { id: "SLEEP-01", title: "Hypnagogic Drift", duration: "30m", goal: "Natural threshold-to-sleep transition" },
            { id: "SLEEP-02", title: "Lucid Dream Induction", duration: "40m", goal: "Conscious dream-entry preparation" },
            { id: "SLEEP-03", title: "Deep Delta", duration: "50m", goal: "Profound restorative rest" }
        ]
    },
    CREA: {
        name: "Creative Cognition",
        description: "Enhance creative insight and pattern disruption",
        protocols: [
            { id: "CREA-01", title: "Creative Incubation", duration: "15m", goal: "Generate creative insights" },
            { id: "CREA-02", title: "Divergent Thinking", duration: "20m", goal: "Expand creative capacity" },
            { id: "CREA-03", title: "Pattern Disruption", duration: "25m", goal: "Break creative blocks" }
        ]
    },
    SENSE: {
        name: "Sensory Perception",
        description: "Refine and expand perceptual capacity",
        protocols: [
            { id: "SENSE-01", title: "Hyper-Perceptual Field", duration: "10m", goal: "Amplify sensory resolution" },
            { id: "SENSE-02", title: "Interoceptive Precision", duration: "15m", goal: "Improve internal signal awareness" },
            { id: "SENSE-03", title: "Synesthetic Mapping", duration: "20m", goal: "Cross-sensory awareness" }
        ]
    },
    META: {
        name: "Self-Model Work",
        description: "Investigate and loosen self-concept",
        protocols: [
            { id: "META-01", title: "Observer Dissolution", duration: "20m", goal: "Loosen rigid self-concepts" },
            { id: "META-02", title: "Identity Redesign", duration: "30m", goal: "Cultivate flexible self-modeling" },
            { id: "META-03", title: "No-Self Inquiry", duration: "35m", goal: "Investigate nature of self" }
        ]
    },
    FLOW: {
        name: "Flow State",
        description: "Access optimal performance consciousness",
        protocols: [
            { id: "FLOW-01", title: "Flow Induction", duration: "18m", goal: "Rapidly access flow state" },
            { id: "FLOW-02", title: "Temporal Expansion", duration: "25m", goal: "Sustained deep immersion with time dilation" }
        ]
    },
    BODY: {
        name: "Somatic Power",
        description: "Embodied presence and physical grounding",
        protocols: [
            { id: "BODY-01", title: "Grounded Power", duration: "15m", goal: "Body-based grounding and presence" },
            { id: "BODY-02", title: "Power Embodiment", duration: "20m", goal: "Embody physical power" }
        ]
    },
    SOC: {
        name: "Social Resonance",
        description: "Interpersonal attunement and connection",
        protocols: [
            { id: "SOC-01", title: "Dyadic Breath Sync", duration: "20m", goal: "Two-person coherence and attunement" },
            { id: "SOC-02", title: "Group Entrainment", duration: "30m", goal: "Collective coherence and synchronization" }
        ]
    },
    PAIN: {
        name: "Pain Modulation",
        description: "Cognitive and attentional pain management",
        protocols: [
            { id: "PAIN-01", title: "Gate Control", duration: "15m", goal: "Modulate pain signals" },
            { id: "PAIN-02", title: "Sensation Reframe", duration: "20m", goal: "Change pain meaning" }
        ]
    },
    SUN: {
        name: "Small Universe",
        description: "Microcosmic orbit training with lower/middle/upper dantian integration",
        protocols: [
            { id: "SUN-01", title: "Small Universe - Beginner Orbit", duration: "18m", goal: "Foundational 6-6 orbit breathing" },
            { id: "SUN-02", title: "Small Universe - Intermediate Orbit", duration: "24m", goal: "6-8 ascent/descent circulation" },
            { id: "SUN-03", title: "Small Universe - Advanced Three Dantian Orbit", duration: "36m", goal: "Long-cycle orbit with dantian emphasis" }
        ]
    }
};
