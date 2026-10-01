# 3. Theoretical Model

This section presents the theoretical framework developed in this study. Section 3.1 introduces the baseline stacked model of a foldable OLED panel (the NPSO model), including its neutral-plane stress formulation and the genetic-algorithm-based thickness optimization. Section 3.2 develops the self-consistent relaxation–plasticity coupled (SCRP) constitutive model, which upgrades the adhesive layer from a linear elastic description to a coupled viscoelastic–viscoplastic one. Section 3.3 develops the cyclic-damage self-evolving (CDSE) interface model, which endows the layer interfaces with progressive damage and cyclic-fatigue capability. Finally, Section 3.4 assembles the two modules into an integrated SCRP–CDSE framework and describes its finite-element implementation.

## 3.1 The NPSO Baseline: Stacked Structure and Neutral-Plane Stress Model

### 3.1.1 Geometric configuration of the stacked panel

The stacked structure of a foldable OLED panel is illustrated in Figure 1, which consists of a cover layer, a glue layer, a passivation layer, a cathode, an OLED layer, an ITO layer, three barrier layers, and a PI substrate [5]. The OLED layer, which governs the luminance and uniformity of the panel, is sandwiched between the cathode and the ITO layer and is therefore the most critical functional layer to be protected. As the panel is symmetrical in structure, only half of the panel is analysed. The schematic diagram of the structure before and after being folded is shown in Figure 2, which is inward folding with a rotation angle of 90 degrees. To realize the folding action, a rigid body is necessary, and it is also included in Figure 2. The length of the foldable OLED panel, the length of the rigid body, and the bending radius are denoted as L, LR, and R, respectively.

The ten layers of the stack are numbered from the top surface downwards, as summarized in Table 1. Each layer is characterized by an elastic modulus Ei, a Poisson's ratio νi, and a thickness di. It is noted that the stack exhibits an alternating hard–soft–hard arrangement, in which the glue layer (Layer 2) is the softest layer of the whole stack. This arrangement is the physical prerequisite that makes the neutral plane tunable [4], and it also defines the entry points at which the modules developed in Sections 3.2 and 3.3 are inserted.

Table 1  Material and geometric parameters of the ten layers of the stacked OLED panel.

| No. | Layer | E (GPa) | ν | Thickness (μm) |
|:--:|:--|:--:|:--:|:--:|
| 1 | Cover | 8.60 | 0.29 | 15 |
| 2 | Glue | 3.20 | 0.45 | 10 |
| 3 | Passivation | 99.51 | 0.30 | 0.4 |
| 4 | Cathode | 70.00 | 0.33 | 0.4 |
| 5 | OLED | 58.60 | 0.30 | 0.4 |
| 6 | ITO | 106.50 | 0.30 | 0.2 |
| 7 | Barrier 1 | 99.51 | 0.30 | 0.4 |
| 8 | Barrier 2 | 69.00 | 0.30 | 0.5 |
| 9 | Barrier 3 | 99.51 | 0.30 | 0.5 |
| 10 | PI | 6.75 | 0.33 | 26 |


### 3.1.2 Neutral-plane stress formulation

When a multilayer stack is bent, a neutral plane exists within the stack at which neither tensile nor compressive stress is generated, and the farther a layer lies from the neutral plane, the higher the bending stress it experiences. Therefore, if the fragile OLED layer can be shifted onto the neutral plane, its stress approaches zero, which is the central idea of neutral-plane engineering [4]. Following the mathematical model of the bending stress experienced by each film of a multilayer stack during bending [6], the stress on each film can be expressed as

$$d_1+d_2+\cdots+d_{n-1}\le z_n\le h:\quad \sigma_n=\bar{E}_n\left[\varepsilon_{bot}+\frac{z_n}{h}\left(\varepsilon_{top}-\varepsilon_{bot}\right)\right] \tag{1a}$$

$$d_1\le z_2\le d_1+d_2:\quad \sigma_2=\bar{E}_2\left[\varepsilon_{bot}+\frac{z_2}{h}\left(\varepsilon_{top}-\varepsilon_{bot}\right)\right] \tag{1b}$$

$$0\le z_1\le d_1:\quad \sigma_1=\bar{E}_1\left[\varepsilon_{bot}+\frac{z_1}{h}\left(\varepsilon_{top}-\varepsilon_{bot}\right)\right] \tag{1c}$$

where Ei represents the elastic modulus of each film, νi represents Poisson's ratio of each film, h is the thickness of the overall foldable panel, zi represents the position of each film in the thickness direction, R is the bending radius, and εtop and εbot represent the bending strain at the top and bottom surfaces of the panel. The bending strains at the two outer surfaces are given by

$$\varepsilon_{bot}=-\frac{1}{2R}\frac{\sum_{i=1}^{n}\bar{E}_i\left(z_i^2-z_{i-1}^2\right)}{\sum_{i=1}^{n}\bar{E}_i\left(z_i-z_{i-1}\right)} \tag{2}$$

$$\varepsilon_{top}=\frac{h}{R}-\frac{1}{2R}\frac{\sum_{i=1}^{n}\bar{E}_i\left(z_i^2-z_{i-1}^2\right)}{\sum_{i=1}^{n}\bar{E}_i\left(z_i-z_{i-1}\right)} \tag{3}$$

where the position of each film and its effective modulus are defined as

$$z_i=\sum_{j=1}^{i}d_j \tag{4}$$

$$\bar{E}_i=\frac{E_i}{1-\nu_i^2} \tag{5}$$

It follows from Equations (1)–(5) that the neutral-plane position, i.e. the weighted centroid of the stack, is

$$z_{np}=\frac{\sum_{i}\bar{E}_i h_i z_i}{\sum_{i}\bar{E}_i h_i} \tag{6}$$

Equation (6) is the mechanical kernel of the NPSO model. In the original formulation, all effective moduli Ēi are treated as constants, so that znp is a fixed quantity determined solely by the geometry and the elastic moduli of the stack.

### 3.1.3 Objective function and thickness optimization

In a foldable OLED panel, the luminance and uniformity are mainly determined by the OLED layer, and the OLED layer is therefore taken as the key functional layer. The reduction of the stress on the OLED layer is beneficial for enhancing the overall reliability of the panel. Accordingly, the OLED layer is chosen as the stress-improvement objective, and the objective function F is defined as

$$F=\left|\bar{E}_{OLED}\left[\varepsilon_{bot}+\frac{z_{OLED}}{h}\left(\varepsilon_{top}-\varepsilon_{bot}\right)\right]\right| \tag{7}$$

$$\bar{E}_{OLED}=\frac{E_{OLED}}{1-\nu_{OLED}^2} \tag{8}$$

Equation (7) represents the stress value on the OLED layer, and a smaller value is preferred. Based on this objective function, the optimal combination of layer thicknesses can be obtained.

Since an almost infinite number of thickness combinations exists, it is almost impossible to simulate all combinations to find an optimal solution. Taking the combination of three layers (cover, glue, and PI) as an example, even if there are only 20 thickness choices for each layer, the total simulation number would reach 8000, which is almost impossible to finish within an acceptable design cycle. A genetic algorithm is therefore introduced to search the optimum configuration of the thickness of each layer [5], which helps to shorten the design time and reduce development risk.

The genetic algorithm is an optimization algorithm that simulates the principles of biological genetic evolution. It combines the principles of "survival of the fittest" with genetic crossover and mutation, encoding the problem to be solved into chromosomes. By simulating the process of biological evolution and performing population iteration, selection, crossover, mutation, and multiple iterations, the algorithm selects the best chromosome, and the solution corresponding to the best chromosome is the optimal solution to the problem.

Considering that the coating process of the OLED layer must not be changed, the thicknesses of the OLED layer, the barrier layers, and the passivation layer are not optimized. Therefore, the thicknesses of the cover layer (dCover), the glue layer (dGlue), and the PI substrate (dPI) are selected as the optimized parameters. The optimization is performed by minimizing Equation (7) subject to the geometric constraint of Equation (1a). The iteration is terminated when no superior solution emerges during the evolutionary process, and the algorithm identifies the optimal solution as the individual with the highest fitness value. The resulting optimal thickness configuration and its corresponding stress distribution are reported in Section 4.

## 3.2 The SCRP Module: Self-Consistent Relaxation–Plasticity Coupled Constitutive Model

The NPSO model treats all ten layers, including the glue layer, as linear elastic and time-independent. In reality, however, the optically clear adhesive (OCA) used as the glue layer exhibits pronounced viscoelastic behaviour such as stress relaxation and creep [9,10,30], and it additionally develops irrecoverable deformation under sustained load. To remove this simplification, the SCRP module replaces the constant modulus of the glue layer with a coupled viscoelastic–viscoplastic constitutive description. The module retains the standard generalized Maxwell framework as its viscoelastic backbone [11] and adopts the Qian–Liu framework as its viscoplastic counterpart [45]; the modification introduced in this study lies in the coupling between the two mechanisms, as detailed in Sections 3.2.3 and 3.2.4.

### 3.2.1 Viscoelastic part: generalized Maxwell model and Prony series

OCA exhibits typical viscoelastic mechanical behaviours such as stress relaxation and creep, which can be effectively characterized by establishing an appropriate viscoelastic constitutive model. Commonly used viscoelastic models in related studies include the Maxwell model, the generalized Maxwell model, the Kelvin model, and various four-parameter models [11]. In this study, Hookean springs and dashpots are adopted as the fundamental rheological elements, representing ideal elastic solids and viscous fluids, respectively, and the generalized Maxwell model is selected to analyse the viscoelastic behaviour of the glue layer.

As illustrated in Figure 3, the generalized Maxwell model consists of several Maxwell elements arranged in parallel with an additional spring to capture relaxation behaviour. Under constant applied strain, the stress response of a basic Maxwell element can be expressed as

$$\sigma(t)=\varepsilon_0 E e^{-t/\tau} \tag{9}$$

where E is the elastic modulus of the spring, ε0 is the applied strain, and τ = η/E represents the relaxation time constant of the element. Since all units connected in parallel undergo the same strain while the total stress is the summation of the stresses carried by each unit, the stress–strain relationship of the generalized Maxwell model can be expressed as

$$\sigma=\sigma_1+\sigma_2+\cdots+\sigma_n,\qquad \varepsilon=\varepsilon_1=\varepsilon_2=\cdots=\varepsilon_n \tag{10}$$

The stress relaxation modulus of the generalized Maxwell model can be expressed as

$$E(t)=E_\infty+\sum_{i=1}^{N}E_i e^{-t/\tau_i} \tag{11}$$

where E∞ is the long-term modulus and Ei represents the contribution of the i-th Maxwell element. The normalized modulus gi is frequently employed as a dimensionless descriptor of the material constants and, together with the relaxation time τi, constitutes the Prony series, which is widely used for defining viscoelastic properties and for numerical implementation. The expression for the normalized modulus is given by

$$g(t)=1-\sum_{i=1}^{N}g_i\left(1-e^{-t/\tau_i}\right) \tag{12}$$

According to the Boltzmann superposition principle, the stress response of the generalized Maxwell model under an arbitrary loading history can be expressed as

$$\sigma(t)=\varepsilon_0 E(t)+\int_{0}^{t}E(t-\xi)\frac{d\varepsilon(\xi)}{d\xi}\,d\xi \tag{13}$$

### 3.2.2 Viscoplastic part: the original Qian–Liu framework

To describe the irrecoverable deformation of the glue layer, the Qian–Liu model is adopted [45]. As a damage-coupled unified viscoplastic constitutive framework grounded in irreversible thermodynamics, it enables the coupling of elastic and viscoplastic damage and effectively captures time- and rate-dependent viscoplastic deformation, complex loading histories, and creep–fatigue interactions; it is therefore well suited for describing the viscoplastic response of OCA. The general form of the Qian–Liu viscoplastic model is given by

$$\dot{\varepsilon}^{I}=\Theta(T)\left[\sinh\left(\frac{\sigma-X_1-X_2}{D}\right)\right]^{n} \tag{14}$$

$$X_k=\frac{A\sigma_{ss}}{A_k}\left[1-\exp\left(-\frac{A_k H_k}{A\sigma_{ss}}\varepsilon^{I}\right)\right]\quad(k=1,2) \tag{15}$$

where Θ(T) denotes the thermal activation term, whose explicit expression is

$$\Theta(T)=\dot{\varepsilon}_0\exp\left(-\frac{Q}{kT}\right) \tag{16}$$

In this formulation, the back stresses X1 and X2 are introduced to capture the short- and long-range components of dislocation-mediated internal stress; ε̇I and εI denote the inelastic strain rate and inelastic strain, respectively; Q is the apparent activation energy; T is the absolute temperature; D is the drag stress; σss is the saturation stress; H1 and H2 are the strain-hardening coefficients; and A, A1, and A2 are the back-stress coefficients.

It should be noted that the two back stresses in Equation (15) were originally introduced to represent dislocation-mediated internal stress, i.e. the plastic mechanism of metals, whereas the glue layer calibrated in this study is a crosslinked polymer whose irrecoverable deformation is dominated by chain-segment sliding. The original framework therefore borrows a metal plasticity mechanism to interpret a polymer mechanism, which is the physical gap addressed by Modification II in Section 3.2.4.

### 3.2.3 Modification I: coupling the viscoplastic flow to the relaxed effective stress

In the original framework, the total strain is decomposed into viscoelastic and viscoplastic components, which are assumed to be uncoupled:

$$\varepsilon_{total}=\varepsilon_{ve}+\varepsilon_{vp} \tag{17}$$

Under this assumption, the viscoelastic part relaxes according to its own timescale while the viscoplastic part is driven by the instantaneous stress σ, so that the two mechanisms do not inform each other. In long-term or elevated-temperature service, however, the modulus of the glue layer itself relaxes with time. If the instantaneous stress is still used to drive the viscoplastic flow, the driving stress is overestimated, and the resulting plastic deformation is physically inconsistent.

To remove this inconsistency, the present study replaces the instantaneous driving stress by a relaxed effective stress obtained from the Boltzmann convolution, thereby establishing a self-consistent coupling between the viscoelastic and viscoplastic mechanisms:

$$\dot{\varepsilon}^{vp}=\Theta(T)\left[\sinh\left(\frac{\sigma_{eff}(t)-X}{D}\right)\right]^{n} \tag{18}$$

$$\sigma_{eff}(t)=\int_{0}^{t}E(t-\xi)\,\dot{\varepsilon}(\xi)\,d\xi \tag{19}$$

Since the relaxed effective stress is lower than the instantaneous stress, the driving force of the viscoplastic flow is reduced, the plastic deformation saturates earlier, and the long-term peak stress predicted for the glue layer is correspondingly lower. The direction of the improvement is thus determinate rather than a matter of parameter tuning.

### 3.2.4 Modification II: single back stress with a detrapping stress

Since the target material is a crosslinked polymer rather than a metal, the two dislocation-based back stresses of the original framework are merged into a single back stress X, and the hyperbolic-sine flow rule is replaced by a threshold power law in which a detrapping stress σ0 represents the critical internal stress at which the constraint of the polymer network is released:

$$X=X_c\left[1-e^{-\kappa\varepsilon^{vp}}\right] \tag{20}$$

$$\dot{\varepsilon}^{vp}=\Theta(T)\left\langle\frac{\left|\sigma_{eff}-X\right|-\sigma_0}{D}\right\rangle^{m}\mathrm{sgn}\left(\sigma_{eff}-X\right) \tag{21}$$

where Xc and κ are the saturation value and the evolution rate of the back stress, σ0 is the detrapping stress, and m is the power-law exponent. Equations (18)–(21) constitute the SCRP constitutive model: the viscoelastic backbone of Equations (11)–(13) is retained, while the viscoplastic flow is resolved with a coupled, polymer-appropriate description. The coupling term of Equation (19) and the detrapping stress of Equation (21) are the two modifications that distinguish the SCRP module from the original framework.

The SCRP model is calibrated by stress-relaxation and creep experiments, from which the Prony parameters gi and τi and the viscoplastic parameters Xc, κ, σ0, and m are identified. Once calibrated, the modulus of the glue layer is no longer a constant but a time- and temperature-dependent quantity E(t, T). Substituting this quantity into Equation (6) makes the neutral-plane position a function of time, znp(t), which is the central physical consequence of the SCRP module: the neutral plane that the NPSO model computed as static becomes a drifting neutral plane.

## 3.3 The CDSE Module: Cyclic-Damage Self-Evolving Interface Model

The NPSO model implicitly assumes that adjacent layers are perfectly bonded, i.e. that the displacement and stress are continuous across every interface. In reality, the interfaces of a foldable panel slide and progressively debond under repeated bending, and this subcritical interfacial degradation is a primary cause of delamination. To remove this simplification, the CDSE module inserts a traction–separation relationship at the critical interfaces and lets it degrade with cyclic loading. The module adopts the conventional bilinear cohesive zone model as its backbone [12] and introduces two modifications: a dual damage criterion (Section 3.3.3) and a mixed-mode fracture criterion (Section 3.3.4).

### 3.3.1 Bilinear traction–separation law

This study employs the bilinear traction–separation law (Figure 4) to describe the debonding process occurring at the layer interfaces [12]. In the initial stage, the interface exhibits an elastic response, with shear stress increasing linearly with displacement, controlled by the initial stiffness K0. The stress reaches a peak σmax at the critical displacement δi = σmax/K0. Thereafter, damage begins and develops, causing the shear stress to decrease gradually until complete separation occurs at the displacement δf, beyond which the stress drops to zero and remains constant, indicating that the interface has completely debonded. The law is written as

$$\sigma=\begin{cases}K_0\,\delta, & \delta\le\delta_i\\[4pt]\sigma_{max}\dfrac{\delta_f-\delta}{\delta_f-\delta_i}, & \delta_i<\delta<\delta_f\\[4pt]0, & \delta\ge\delta_f\end{cases} \tag{22}$$

The area enclosed by the traction–separation curve quantifies the energy required for complete fracture of the interface, commonly referred to as the fracture energy or interface toughness:

$$\Gamma=\frac{1}{2}\sigma_{max}\delta_f \tag{23}$$

To characterize the progressive degradation of interfacial strength over time, a damage variable D is introduced when the separation displacement δ exceeds the initiation value δi but remains below the final value δf. This variable ranges from 0 (undamaged) to 1 (fully damaged) and is defined as a function of the maximum separation displacement δmax experienced during loading:

$$D=\frac{\delta_f\left(\delta-\delta_i\right)}{\delta\left(\delta_f-\delta_i\right)} \tag{24}$$

It effectively scales the stiffness of the interface, so that the current traction is given by a modified linear relation with reduced stiffness:

$$\sigma=(1-D)K_0\delta \tag{25}$$

During unloading, δmax remains unchanged, and thus the damage variable also remains constant, reflecting the irreversibility of interfacial damage.

### 3.3.2 Shear-lag analysis for interfacial slip

To connect the interface constitutive law back to the layer stresses of the NPSO model, a shear-lag analysis is performed [12]. The relative displacement at the interface is given by δ = um − ux, where um is the end displacement prescribed on the top surface of the block and ux is the axial displacement of the layer, with um ≥ 0 based on the assumption that the substrate behaves as a rigid material. For each infinitesimal element of the layer, the difference in axial stress σx between two cross sections is balanced by the interfacial shear stress, so that force equilibrium requires

$$\sigma_t=-B\frac{d\sigma_x}{dx} \tag{26}$$

where B is the thickness of the layer, and the axial stress is related to its axial displacement through the linear elastic Hooke's law:

$$\sigma_x=E_x\frac{du_x}{dx} \tag{27}$$

The effective elastic modulus in the x-direction of the multilayer block is calculated based on the rule of mixtures (Voigt model):

$$E_x=\frac{\sum_{i}E_i t_i}{\sum_{i}t_i} \tag{28}$$

where Ei and ti are the elastic modulus and thickness of the i-th layer in the block. In the linear elastic stage, the governing equation admits the closed-form solution

$$\delta=D\,\frac{\cosh\left(x/\lambda\right)}{\cosh\left(H/\lambda\right)},\qquad \lambda=\sqrt{\frac{B E_x}{K_0}} \tag{29}$$

where λ is the characteristic length and H is the initial height of the specimen. The corresponding indentation force is given by

$$P=\frac{E_x A B}{\lambda}\tanh\left(\frac{x}{\lambda}\right) \tag{30}$$

Equations (26)–(30) weld the interface constitutive law to the layer stresses: the interfacial slip δ not only depends on the layer stress σx but also feeds back into it. This is precisely the format through which the CDSE module is coupled into the NPSO model.

### 3.3.3 Modification I: dual (monotonic plus cyclic) damage criterion

The classical formulation triggers damage only when the relative displacement reaches a critical initiation value. This displacement-based criterion cannot represent subcritical cyclic sliding: as long as the amplitude of the repeated bending remains below δi, the interface is regarded as intact, whereas in reality tens of thousands of subcritical cycles are the dominant cause of delamination. To endow the model with fatigue-life prediction capability, the damage criterion is extended from a single displacement-triggered route to a dual criterion in which the monotonic damage and the cyclic accumulated damage are combined by taking their maximum:

$$D=\max\left[\,D_{mono}\left(\delta_{max}\right),\ D_{cyc}\left(N\right)\,\right] \tag{31}$$

$$D_{cyc}(N)=\int_{0}^{N}\frac{dD}{dN}\,dN \tag{32}$$

$$\frac{dD}{dN}=c\left(\frac{\Delta G}{G_c}\right)^{m} \tag{33}$$

where ΔG is the amplitude of the interfacial energy release rate per bending cycle, Gc = Γ is the interface fracture energy of Equation (23), and c and m are two newly calibrated parameters, with m acting as the fatigue exponent and taking a form of the same family as the Coffin–Manson or Paris law [41]. Because the interfacial shear traction of the cohesive law is linear in the relative slip, the amplitude of the energy release rate is proportional to the square of the interfacial slip range, ΔG ∝ (Δδ)², so that a modest reduction of the slip corresponds to a proportionally larger reduction of the driving force; this relation is what couples the CDSE module to the SCRP module in Section 4.3.2. Under this criterion, the interface accumulates damage even when every individual cycle remains below the static initiation threshold, so that degradation proceeds below the critical value.

### 3.3.4 Modification II: mixed-mode (mode I/II) fracture criterion

The original model was calibrated under an indentation condition in which the interface is purely sheared (mode II). During the bending of a laminated panel, however, the interface is simultaneously opened in the normal direction (mode I, particularly on the outer side of the bend) and slid in the tangential direction (mode II). To match the bending load case, a mixed-mode fracture criterion is therefore adopted [12,39]:

$$\left(\frac{G_{I}}{G_{Ic}}\right)^{\alpha}+\left(\frac{G_{II}}{G_{IIc}}\right)^{\alpha}=1 \tag{34}$$

where α is the mode-mixity parameter (with α = 1 corresponding to a linear mixture) and GIc and GIIc are the interfacial fracture energies of the two modes. Equations (22)–(25), together with the dual criterion of Equations (31)–(33) and the mixed-mode criterion of Equation (34), constitute the CDSE interface model. The cyclic damage accumulation and the mixed-mode criterion are the two modifications that distinguish the CDSE module from the conventional cohesive zone model.

The CDSE parameters K0, σmax, δf, and the fracture energies are obtained by calibrating the model against interfacial mechanical tests, and the cyclic parameters c and m are identified from repeated-bending experiments. Because damage now accumulates with cycle number, the model no longer predicts a single instantaneous stress but a failure life Nf, i.e. the number of cycles after which a given interface reaches full debonding.

## 3.4 The Coupled SCRP–CDSE Framework: Layer-Wise and Interface-Wise Integration

### 3.4.1 Module placement

The two modules are integrated into the NPSO model at two distinct and non-overlapping locations, as illustrated in Figure 5. The SCRP module is inserted inside the stack by replacing the constant modulus of the glue layer (Layer 2, the softest layer) with the time- and temperature-dependent modulus E(t, T) provided by Equations (18)–(21), while the moduli of the other nine layers are left unchanged. The CDSE module is inserted between the layers by replacing the ideal-bonding assumption at the critical interfaces with the traction–separation relation of Equations (22)–(25), in which the interfacial slip is resolved by the shear-lag solution of Equations (26)–(30).

This placement gives the integrated SCRP–CDSE framework a clear division of labour: the SCRP module governs the in-layer material behaviour of the glue layer, whereas the CDSE module governs the inter-layer damage and delamination, so that the two modules occupy the layer interior and the layer interface respectively without competing for the same location. Because both modules are inserted at the entry parameters of the data flow of the NPSO model, i.e. at the layer moduli and at the inter-layer connection assumption, the integration is achieved by two local substitutions and does not require re-deriving the neutral-plane formulation of Equations (1)–(6).

### 3.4.2 Numerical implementation

The coupled SCRP–CDSE framework is implemented in a commercial finite-element package. The SCRP constitutive model is implemented through a user-defined material subroutine, in which the Prony series of Equation (12) and the effective-stress coupling of Equation (19) are integrated in time, and the viscoplastic flow of Equation (21) is solved by a backward-Euler return mapping [11]. The CDSE is implemented through surface-based cohesive interactions at the selected interfaces, with the bilinear traction–separation law of Equation (22) and the cyclic damage accumulation of Equation (33) evaluated once per loading cycle [12]. The geometric model reproduces the ten-layer stack of Figure 1 with the same layer thicknesses and boundary conditions adopted for the NPSO model, and the same bending radius R is prescribed so that the results of the NPSO model, the NPSO–SCRP model, the NPSO–CDSE model, and the SCRP–CDSE framework are directly comparable. A mesh-sensitivity study is performed to confirm that the computed layer stress and the interfacial slip are independent of the mesh size.

Within this numerical framework, two quantities are extracted for comparison. The first is the layer stress σn of Equation (1), and in particular the stress on the OLED layer; the second is the interfacial damage D of Equation (31) and the associated failure life Nf. The NPSO model predicts only the instantaneous stress of a statically neutral plane, whereas the SCRP–CDSE framework predicts both the drift of the neutral plane in time, znp(t), and the evolution of interfacial damage with cycle number, so that the assessment of the foldable panel is extended from an instantaneous stress state to a long-term reliability measure.
